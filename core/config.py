import os
from collections import ChainMap
from functools import lru_cache
from typing import Any, Dict, List, Literal, Optional

import tomli
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class ParserXMLSettings(BaseModel):
    max_tokens: int = 350
    preferred_unit_tags: List[str] = ["SECTION", "Section", "Article", "clause"]
    ignore_tags: List[str] = ["TOC", "INDEX"]


class Settings(BaseSettings):
    """Morphik configuration settings."""

    # Environment variables
    JWT_SECRET_KEY: str
    SESSION_SECRET_KEY: str
    POSTGRES_URI: Optional[str] = None
    UNSTRUCTURED_API_KEY: Optional[str] = None
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ASSEMBLYAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    TURBOPUFFER_API_KEY: Optional[str] = None

    # API configuration
    HOST: str
    PORT: int
    RELOAD: bool
    SENTRY_DSN: Optional[str] = None
    # Morphik Embedding API server configuration
    MORPHIK_EMBEDDING_API_KEY: Optional[str] = None
    MORPHIK_EMBEDDING_API_DOMAIN: str

    # Auth configuration
    JWT_ALGORITHM: str
    dev_mode: bool = False
    dev_entity_type: str = "developer"
    dev_entity_id: str = "dev_user"
    dev_permissions: list = ["read", "write", "admin"]

    # Registered models configuration
    REGISTERED_MODELS: Dict[str, Dict[str, Any]] = {}

    # Completion configuration
    COMPLETION_PROVIDER: Literal["litellm"] = "litellm"
    COMPLETION_MODEL: str

    # Agent configuration
    AGENT_MODEL: str

    # Document analysis configuration
    DOCUMENT_ANALYSIS_MODEL: str

    # Database configuration
    DATABASE_PROVIDER: Literal["postgres"]
    DATABASE_NAME: Optional[str] = None
    # Database connection pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_TIMEOUT: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_MAX_RETRIES: int = 3
    DB_RETRY_DELAY: float = 1.0

    # Embedding configuration
    EMBEDDING_PROVIDER: Literal["litellm"] = "litellm"
    EMBEDDING_MODEL: str
    VECTOR_DIMENSIONS: int
    EMBEDDING_SIMILARITY_METRIC: Literal["cosine", "dotProduct"]

    # Parser configuration
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    USE_UNSTRUCTURED_API: bool
    FRAME_SAMPLE_RATE: Optional[int] = None
    USE_CONTEXTUAL_CHUNKING: bool = False
    PARSER_XML: ParserXMLSettings = ParserXMLSettings()

    # Rules configuration
    RULES_PROVIDER: Literal["litellm"] = "litellm"
    RULES_MODEL: str
    RULES_BATCH_SIZE: int = 4096

    # Graph configuration
    GRAPH_MODE: Literal["local", "api"] = "local"
    GRAPH_PROVIDER: Literal["litellm"] = "litellm"
    GRAPH_MODEL: Optional[str] = None
    ENABLE_ENTITY_RESOLUTION: Optional[bool] = None
    # Graph API configuration
    MORPHIK_GRAPH_API_KEY: Optional[str] = None
    MORPHIK_GRAPH_BASE_URL: Optional[str] = None

    # Reranker configuration
    USE_RERANKING: bool
    RERANKER_PROVIDER: Optional[Literal["flag"]] = None
    RERANKER_MODEL: Optional[str] = None
    RERANKER_QUERY_MAX_LENGTH: Optional[int] = None
    RERANKER_PASSAGE_MAX_LENGTH: Optional[int] = None
    RERANKER_USE_FP16: Optional[bool] = None
    RERANKER_DEVICE: Optional[str] = None

    # Storage configuration
    STORAGE_PROVIDER: Literal["local", "aws-s3"]
    STORAGE_PATH: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None

    # Vector store configuration
    VECTOR_STORE_PROVIDER: Literal["pgvector"]
    VECTOR_STORE_DATABASE_NAME: Optional[str] = None

    # Multivector store configuration
    MULTIVECTOR_STORE_PROVIDER: Literal["postgres", "morphik"] = "postgres"
    # Enable dual ingestion to both fast and slow multivector stores during migration
    ENABLE_DUAL_MULTIVECTOR_INGESTION: bool = False

    # Colpali configuration
    ENABLE_COLPALI: bool
    # Colpali embedding mode: off, local, or api
    COLPALI_MODE: Literal["off", "local", "api"] = "local"

    # Mode configuration
    MODE: Literal["cloud", "self_hosted"] = "cloud"

    # API configuration
    API_DOMAIN: str = "api.morphik.ai"

    # PDF Viewer configuration
    PDF_VIEWER_FRONTEND_URL: Optional[str] = "https://morphik.ai/api/pdf"

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Telemetry configuration
    TELEMETRY_ENABLED: bool = True
    HONEYCOMB_ENABLED: bool = True
    HONEYCOMB_ENDPOINT: str = "https://api.honeycomb.io"
    HONEYCOMB_PROXY_ENDPOINT: str = "https://otel-proxy.onrender.com/"
    SERVICE_NAME: str = "morphik-core"
    OTLP_TIMEOUT: int = 10
    OTLP_MAX_RETRIES: int = 3
    OTLP_RETRY_DELAY: int = 1
    OTLP_MAX_EXPORT_BATCH_SIZE: int = 512
    OTLP_SCHEDULE_DELAY_MILLIS: int = 5000
    OTLP_MAX_QUEUE_SIZE: int = 2048

    # Workflows configuration
    WORKFLOW_MODEL: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    load_dotenv(override=True)

    # Load config.toml
    with open("morphik.toml", "rb") as f:
        config = tomli.load(f)

    em = "'{missing_value}' needed if '{field}' is set to '{value}'"
    openai_config = {}

    # load api config
    api_config = {
        "HOST": config["api"]["host"],
        "PORT": int(config["api"]["port"]),
        "RELOAD": bool(config["api"]["reload"]),
        "SENTRY_DSN": os.getenv("SENTRY_DSN", None),
    }

    # load auth config
    auth_config = {
        "JWT_ALGORITHM": config["auth"]["jwt_algorithm"],
        "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", "dev-secret-key"),  # Default for dev mode
        "SESSION_SECRET_KEY": os.environ.get("SESSION_SECRET_KEY", "super-secret-dev-session-key"),
        "dev_mode": config["auth"].get("dev_mode", False),
        "dev_entity_type": config["auth"].get("dev_entity_type", "developer"),
        "dev_entity_id": config["auth"].get("dev_entity_id", "dev_user"),
        "dev_permissions": config["auth"].get("dev_permissions", ["read", "write", "admin"]),
    }

    # Only require JWT_SECRET_KEY in non-dev mode
    if not auth_config["dev_mode"] and "JWT_SECRET_KEY" not in os.environ:
        raise ValueError("JWT_SECRET_KEY is required when dev_mode is disabled")
    # Also require SESSION_SECRET_KEY in non-dev mode
    if not auth_config["dev_mode"] and "SESSION_SECRET_KEY" not in os.environ:
        # Or, if we want to be more strict and always require it via ENV:
        # if "SESSION_SECRET_KEY" not in os.environ:
        #     raise ValueError("SESSION_SECRET_KEY environment variable is required.")
        # For now, align with JWT_SECRET_KEY's dev mode leniency.
        pass  # Dev mode has a default, production should use ENV.

    # Load registered models if available
    registered_models = {}
    if "registered_models" in config:
        registered_models = {"REGISTERED_MODELS": config["registered_models"]}

    # load completion config
    completion_config = {
        "COMPLETION_PROVIDER": "litellm",
    }

    # Set the model key for LiteLLM
    if "model" not in config["completion"]:
        raise ValueError("'model' is required in the completion configuration")
    completion_config["COMPLETION_MODEL"] = config["completion"]["model"]

    # load agent config
    agent_config = {"AGENT_MODEL": config["agent"]["model"]}
    if "model" not in config["agent"]:
        raise ValueError("'model' is required in the agent configuration")

    # load database config
    database_config = {
        "DATABASE_PROVIDER": config["database"]["provider"],
        "DATABASE_NAME": config["database"].get("name", None),
        # Add database connection pool settings
        "DB_POOL_SIZE": config["database"].get("pool_size", 20),
        "DB_MAX_OVERFLOW": config["database"].get("max_overflow", 30),
        "DB_POOL_RECYCLE": config["database"].get("pool_recycle", 3600),
        "DB_POOL_TIMEOUT": config["database"].get("pool_timeout", 10),
        "DB_POOL_PRE_PING": config["database"].get("pool_pre_ping", True),
        "DB_MAX_RETRIES": config["database"].get("max_retries", 3),
        "DB_RETRY_DELAY": config["database"].get("retry_delay", 1.0),
    }
    if database_config["DATABASE_PROVIDER"] != "postgres":
        prov = database_config["DATABASE_PROVIDER"]
        raise ValueError(f"Unknown database provider selected: '{prov}'")

    if "POSTGRES_URI" in os.environ:
        database_config.update({"POSTGRES_URI": os.environ["POSTGRES_URI"]})
    else:
        msg = em.format(missing_value="POSTGRES_URI", field="database.provider", value="postgres")
        raise ValueError(msg)

    # load embedding config
    embedding_config = {
        "EMBEDDING_PROVIDER": "litellm",
        "VECTOR_DIMENSIONS": config["embedding"]["dimensions"],
        "EMBEDDING_SIMILARITY_METRIC": config["embedding"]["similarity_metric"],
    }

    # Set the model key for LiteLLM
    if "model" not in config["embedding"]:
        raise ValueError("'model' is required in the embedding configuration")
    embedding_config["EMBEDDING_MODEL"] = config["embedding"]["model"]

    # load parser config
    parser_config = {
        "CHUNK_SIZE": config["parser"]["chunk_size"],
        "CHUNK_OVERLAP": config["parser"]["chunk_overlap"],
        "USE_UNSTRUCTURED_API": config["parser"]["use_unstructured_api"],
        "USE_CONTEXTUAL_CHUNKING": config["parser"].get("use_contextual_chunking", False),
    }

    # load parser XML config
    if "xml" in config["parser"]:
        xml_config = config["parser"]["xml"]
        parser_config["PARSER_XML"] = ParserXMLSettings(
            max_tokens=xml_config.get("max_tokens", 350),
            preferred_unit_tags=xml_config.get("preferred_unit_tags", ["SECTION", "Section", "Article", "clause"]),
            ignore_tags=xml_config.get("ignore_tags", ["TOC", "INDEX"]),
        )
    if parser_config["USE_UNSTRUCTURED_API"] and "UNSTRUCTURED_API_KEY" not in os.environ:
        msg = em.format(missing_value="UNSTRUCTURED_API_KEY", field="parser.use_unstructured_api", value="true")
        raise ValueError(msg)
    elif parser_config["USE_UNSTRUCTURED_API"]:
        parser_config.update({"UNSTRUCTURED_API_KEY": os.environ["UNSTRUCTURED_API_KEY"]})

    # load reranker config
    reranker_config = {"USE_RERANKING": config["reranker"]["use_reranker"]}
    if reranker_config["USE_RERANKING"]:
        reranker_config.update(
            {
                "RERANKER_PROVIDER": config["reranker"]["provider"],
                "RERANKER_MODEL": config["reranker"]["model_name"],
                "RERANKER_QUERY_MAX_LENGTH": config["reranker"]["query_max_length"],
                "RERANKER_PASSAGE_MAX_LENGTH": config["reranker"]["passage_max_length"],
                "RERANKER_USE_FP16": config["reranker"]["use_fp16"],
                "RERANKER_DEVICE": config["reranker"]["device"],
            }
        )

    # load storage config
    storage_config = {
        "STORAGE_PROVIDER": config["storage"]["provider"],
        "STORAGE_PATH": config["storage"]["storage_path"],
    }
    match storage_config["STORAGE_PROVIDER"]:
        case "local":
            storage_config.update({"STORAGE_PATH": config["storage"]["storage_path"]})
        case "aws-s3" if all(key in os.environ for key in ["AWS_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY"]):
            storage_config.update(
                {
                    "AWS_REGION": config["storage"]["region"],
                    "S3_BUCKET": config["storage"]["bucket_name"],
                    "AWS_ACCESS_KEY": os.environ["AWS_ACCESS_KEY"],
                    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
                }
            )
        case "aws-s3":
            msg = em.format(missing_value="AWS credentials", field="storage.provider", value="aws-s3")
            raise ValueError(msg)
        case _:
            prov = storage_config["STORAGE_PROVIDER"]
            raise ValueError(f"Unknown storage provider selected: '{prov}'")

    # load vector store config
    vector_store_config = {"VECTOR_STORE_PROVIDER": config["vector_store"]["provider"]}
    if vector_store_config["VECTOR_STORE_PROVIDER"] != "pgvector":
        prov = vector_store_config["VECTOR_STORE_PROVIDER"]
        raise ValueError(f"Unknown vector store provider selected: '{prov}'")

    if "POSTGRES_URI" not in os.environ:
        msg = em.format(missing_value="POSTGRES_URI", field="vector_store.provider", value="pgvector")
        raise ValueError(msg)

    # load rules config
    rules_config = {
        "RULES_PROVIDER": "litellm",
        "RULES_BATCH_SIZE": config["rules"]["batch_size"],
    }

    # Set the model key for LiteLLM
    if "model" not in config["rules"]:
        raise ValueError("'model' is required in the rules configuration")
    rules_config["RULES_MODEL"] = config["rules"]["model"]

    # load morphik config
    morphik_config = {
        "ENABLE_COLPALI": config["morphik"]["enable_colpali"],
        "COLPALI_MODE": config["morphik"].get("colpali_mode", "local"),
        "MODE": config["morphik"].get("mode", "cloud"),  # Default to "cloud" mode
        # API domain for core server
        "API_DOMAIN": config["morphik"].get("api_domain", "api.morphik.ai"),
        # Domain for Morphik embedding API
        "MORPHIK_EMBEDDING_API_DOMAIN": config["morphik"].get(
            "morphik_embedding_api_domain", config["morphik"].get("api_domain", "api.morphik.ai")
        ),
    }

    # load pdf viewer config
    pdf_viewer_config = {}
    if "pdf_viewer" in config:
        pdf_viewer_config = {
            "PDF_VIEWER_FRONTEND_URL": config["pdf_viewer"].get("frontend_url", "https://morphik.ai/api/pdf")
        }

    # Redis config is now only read from environment variables
    redis_config = {}

    # load graph config
    graph_config = (
        {
            "GRAPH_MODE": "local",
            "GRAPH_PROVIDER": "litellm",
            "ENABLE_ENTITY_RESOLUTION": config["graph"].get("enable_entity_resolution", True),
        }
        if config["graph"].get("mode", "local") == "local"
        else {
            "GRAPH_MODE": "api",
            "MORPHIK_GRAPH_BASE_URL": config["graph"].get("base_url", "https://graph-api.morphik.ai"),
            "MORPHIK_GRAPH_API_KEY": os.environ.get("MORPHIK_GRAPH_API_KEY", None),
        }
    )

    # Set the model key for LiteLLM
    if "model" not in config["graph"]:
        raise ValueError("'model' is required in the graph configuration")
    graph_config["GRAPH_MODEL"] = config["graph"]["model"]

    # load document analysis config
    document_analysis_config = {}
    if "document_analysis" in config:
        document_analysis_config = {"DOCUMENT_ANALYSIS_MODEL": config["document_analysis"]["model"]}

    # load telemetry config
    telemetry_config = {}
    if "telemetry" in config:
        telemetry_config = {
            "TELEMETRY_ENABLED": config["telemetry"].get("enabled", True),
            "HONEYCOMB_ENABLED": config["telemetry"].get("honeycomb_enabled", True),
            "HONEYCOMB_ENDPOINT": config["telemetry"].get("honeycomb_endpoint", "https://api.honeycomb.io"),
            "SERVICE_NAME": config["telemetry"].get("service_name", "morphik-core"),
            "OTLP_TIMEOUT": config["telemetry"].get("otlp_timeout", 10),
            "OTLP_MAX_RETRIES": config["telemetry"].get("otlp_max_retries", 3),
            "OTLP_RETRY_DELAY": config["telemetry"].get("otlp_retry_delay", 1),
            "OTLP_MAX_EXPORT_BATCH_SIZE": config["telemetry"].get("otlp_max_export_batch_size", 512),
            "OTLP_SCHEDULE_DELAY_MILLIS": config["telemetry"].get("otlp_schedule_delay_millis", 5000),
            "OTLP_MAX_QUEUE_SIZE": config["telemetry"].get("otlp_max_queue_size", 2048),
        }

    # load workflows config
    workflows_config = {}
    if "workflows" in config and "model" in config["workflows"]:
        workflows_config = {
            "WORKFLOW_MODEL": config["workflows"]["model"],
        }

    # load multivector store config
    multivector_store_config = {}
    if "multivector_store" in config:
        multivector_store_config = {
            "MULTIVECTOR_STORE_PROVIDER": config["multivector_store"].get("provider", "postgres"),
        }

        # Check for Turbopuffer API key if using morphik provider
        if multivector_store_config["MULTIVECTOR_STORE_PROVIDER"] == "morphik":
            if "TURBOPUFFER_API_KEY" not in os.environ:
                msg = em.format(
                    missing_value="TURBOPUFFER_API_KEY", field="multivector_store.provider", value="morphik"
                )
                raise ValueError(msg)
            multivector_store_config["TURBOPUFFER_API_KEY"] = os.environ["TURBOPUFFER_API_KEY"]

    settings_dict = dict(
        ChainMap(
            api_config,
            auth_config,
            registered_models,
            completion_config,
            agent_config,
            database_config,
            embedding_config,
            parser_config,
            reranker_config,
            storage_config,
            vector_store_config,
            multivector_store_config,
            rules_config,
            morphik_config,
            pdf_viewer_config,
            redis_config,
            graph_config,
            document_analysis_config,
            telemetry_config,
            workflows_config,
            openai_config,
        )
    )

    return Settings(**settings_dict)
