def get_framework_signature(self) -> FrameworkSignature:
        return FrameworkSignature(
            supported_tasks=[
                TaskType.TEXT_GENERATION,
                TaskType.YoutubeING,
                TaskType.CREATIVE_WRITING,
                TaskType.CODE_ASSISTANCE,
                TaskType.ANALYSIS,
                TaskType.SUMMARIZATION
            ],
            security_features=[
                SecurityFeature.PROMPT_INJECTION_PROTECTION,
                SecurityFeature.INPUT_SANITIZATION,
            ],
            available_models=[
                ModelCapability(
                    provider=ModelProvider.GOOGLE_GEMINI,
                    model_name="gemini-pro",
                    is_active=os.getenv('MODEL_TYPE', 'gemini').lower() == 'gemini',
                    max_tokens=8192,
                    supports_streaming=False,
                    response_time_avg_ms=2000
                ),
                ModelCapability(
                    provider=ModelProvider.LOCAL_LLAMA,
                    model_name=os.getenv('LOCAL_MODEL_NAME', 'llama3'),
                    is_active=os.getenv('MODEL_TYPE', 'gemini').lower() == 'local',
                    max_tokens=4096,
                    supports_streaming=True,
                    response_time_avg_ms=500
                )
            ],
            api_endpoints=[
                APICapability(
                    endpoint="/",
                    method="GET",
                    description="Health check endpoint",
                    input_schema={},
                    output_schema={"status": "string"},
                    example_request={},
                    example_response={"status": "API is running"}
                ),
                APICapability(
                    endpoint="/v1/delegate-task",
                    method="POST", 
                    description="Delegate task to AI model",
                    input_schema={
                        "prompt": {"type": "string", "required": True}
                    },
                    output_schema={
                        "status": {"type": "string"},
                        "response": {"type": "string"}
                    },
                    example_request={"prompt": "Hello, how are you?"},
                    example_response={
                        "status": "success",
                        "response": "Hello! I'm doing well, thank you for asking."
                    }
                ),
                APICapability(
                    endpoint="/v1/capabilities",
                    method="GET",
                    description="Get framework capabilities and signature",
                    input_schema={},
                    output_schema={"type": "object", "description": "Full capability signature"},
                    example_request={},
                    example_response={"name": "Application Delegation Framework", "version": "1.0.0"}
                )
            ],
            base_url=self.base_url,
            documentation_url=f"{self.base_url}/docs"
        )
