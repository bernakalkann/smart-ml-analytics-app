# AWS Sağlayıcı Tanımı
provider "aws" {
  region = "eu-central-1" # Frankfurt Bölgesi
}

# 1. Model Ağırlıklarının Tutulacağı S3 Bucket (Benzersiz olması için Account ID eklendi)
resource "aws_s3_bucket" "model_bucket" {
  bucket        = "smart-analytics-ml-models-386785029067"
  force_destroy = true # Silerken içindekilerle beraber temizlenmesi için
}

# 1.1. Model Ağırlıklarının S3'e yüklenmesi (SageMaker başlamadan önce yüklenmeli)
resource "aws_s3_object" "model_artifact" {
  bucket = aws_s3_bucket.model_bucket.id
  key    = "models/model.tar.gz"
  source = "model.tar.gz"
  etag   = filemd5("model.tar.gz")
}

# 2. SageMaker IAM Rolü (S3'ten modeli okuyabilmesi için)
resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-execution-role-project3"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# S3 Okuma Yetkisi
resource "aws_iam_role_policy" "sagemaker_s3_policy" {
  name = "sagemaker-s3-read-policy"
  role = aws_iam_role.sagemaker_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.model_bucket.arn,
          "${aws_s3_bucket.model_bucket.arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Yetkisi
resource "aws_iam_role_policy_attachment" "sagemaker_cw_policy" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# ECR Resim Okuma Yetkisi (SageMaker'ın imajı çekebilmesi için)
resource "aws_iam_role_policy_attachment" "sagemaker_ecr_policy" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}


# 3. SageMaker Model Kaynağı
resource "aws_sagemaker_model" "ml_model" {
  name               = "smart-prediction-model"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    image          = "763104351884.dkr.ecr.eu-central-1.amazonaws.com/pytorch-inference:2.0.0-cpu-py310" # AWS Resmi PyTorch Konteyneri (eu-central-1 için)
    model_data_url = "s3://${aws_s3_bucket.model_bucket.id}/models/model.tar.gz"
  }

  depends_on = [
    aws_s3_object.model_artifact
  ]
}

# 4. SageMaker Endpoint Konfigürasyonu (Serverless Inference)
resource "aws_sagemaker_endpoint_configuration" "endpoint_config" {
  name = "smart-prediction-endpoint-config"

  production_variants {
    variant_name          = "AllTraffic"
    model_name            = aws_sagemaker_model.ml_model.name
    
    serverless_config {
      max_concurrency   = 2
      memory_size_in_mb = 3072 # 3GB Ram
    }
  }
}

# 5. Canlı SageMaker Endpoint
resource "aws_sagemaker_endpoint" "endpoint" {
  name                 = "smart-prediction-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.endpoint_config.name
}

# 6. Lambda Rolü (SageMaker Endpoint'ini tetikleyebilmesi için)
resource "aws_iam_role" "lambda_role" {
  name = "lambda-sagemaker-proxy-role-project3"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda'ya SageMaker Çağırma ve Loglama İzni Veren Policy
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda-sagemaker-policy-project3"
  description = "Allows Lambda to invoke SageMaker endpoint and log to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sagemaker:InvokeEndpoint",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# 7. Lambda Proxy Fonksiyonu
resource "aws_lambda_function" "sagemaker_proxy" {
  filename         = "lambda_function.zip" # Önceden paketlenmiş kod
  source_code_hash = filebase64sha256("lambda_function.zip")
  function_name    = "sagemaker-prediction-proxy"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.10"
  timeout          = 60

  environment {
    variables = {
      SAGEMAKER_ENDPOINT_NAME = aws_sagemaker_endpoint.endpoint.name
    }
  }
}

# 8. API Gateway REST API Kurulumu
resource "aws_api_gateway_rest_api" "ml_api" {
  name        = "SmartMLPredictAPI"
  description = "API Gateway for ML Predictions"
}

resource "aws_api_gateway_resource" "predict_resource" {
  rest_api_id = aws_api_gateway_rest_api.ml_api.id
  parent_id   = aws_api_gateway_rest_api.ml_api.root_resource_id
  path_part   = "predict"
}

resource "aws_api_gateway_method" "predict_method" {
  rest_api_id   = aws_api_gateway_rest_api.ml_api.id
  resource_id   = aws_api_gateway_resource.predict_resource.id
  http_method   = "POST"
  authorization = "NONE" # Basit testler için açık tutuldu
}

# API Gateway - Lambda Entegrasyonu (Proxy Integration)
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.ml_api.id
  resource_id             = aws_api_gateway_resource.predict_resource.id
  http_method             = aws_api_gateway_method.predict_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.sagemaker_proxy.invoke_arn
}

# Lambda'ya API Gateway'den tetiklenme izni verilmesi
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sagemaker_proxy.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ml_api.execution_arn}/*/*"
}

# API'yi Canlıya Alma (Deployment)
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on  = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.ml_api.id
}

# API Stage Tanımı
resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.ml_api.id
  stage_name    = "prod"
}

# Çıktı URL'si
output "api_url" {
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/predict"
  description = "Canlı tahmin isteklerinin gönderileceği uç nokta URL'si"
}

# Çıktı S3 Bucket Adı
output "s3_bucket_name" {
  value       = aws_s3_bucket.model_bucket.id
  description = "Model ağırlıklarınızı yükleyeceğiniz S3 Bucket adı"
}
