from pprint import PrettyPrinter
from llama_index.core import ServiceContext
from utils.config import Config

class RAGServiceConfig(Config):
    def __init__(self, config=None):
        super().__init__(
            config_dict=config.config_dict 
            if isinstance(config, Config) else config)
        
        self._llm_config = None
        self._embedder_config = None
        self._text_splitter_config = None
        self._llm_class = None
        self._embedder_class = None
        self._text_splitter_class = None

        if config:
            self.set_service_config(config=self)
        
    def set_service_config(self, config: Config):
        if not self.config_dict:
            self.add_props(config.config_dict)

        self._llm_config = config.base.llm
        self._embedder_config = config.base.embedder
        self._text_splitter_config = config.base.text_splitter

        self._llm_class = self._generate_llm_class(config=config)
        self._embedder_class = self._generate_embedder_class(config=config)
        self._text_splitter_class = self._generate_text_splitter_class(config=config)
        
    def _generate_model_class(self, class_name: str, module_path: str):
        # Import module
        exec(f"import {module_path}")
        whitelist = eval(f"dir({module_path})")
        if class_name in whitelist:
            model = eval(f"{module_path}.{class_name}")
        else:
            raise ValueError(
                f"Given classname, {class_name}, is not in whitelist.")
        
        return model
    
    def _generate_llm_class(self, config: Config):
        # Set up the model class
        llm_class_name = config.base.llm.class_name
        llm_module_path = config.base.llm.module_path
        return self._generate_model_class(
            class_name=llm_class_name,
            module_path=llm_module_path
        )

    def _generate_embedder_class(self, config: Config):
        embedder_class_name = config.base.embedder.class_name
        embedder_module_path = config.base.embedder.module_path
        return self._generate_model_class(
            class_name=embedder_class_name,
            module_path=embedder_module_path
        )
    
    def _generate_text_splitter_class(self, config: Config):
        text_splitter_class_name = config.base.text_splitter.class_name
        text_splitter_module_path = config.base.text_splitter.module_path
        return self._generate_model_class(
            class_name=text_splitter_class_name,
            module_path=text_splitter_module_path
        )
    
    @property
    def llm_class(self):
        return self._llm_class
    
    @property
    def embedder_class(self):
        return self._embedder_class
    
    @property
    def text_splitter_class(self):
        return self._text_splitter_class
    
    @property
    def llm_config(self):
        return self._llm_config
    
    @property
    def embedder_config(self):
        return self._embedder_config
    
    @property
    def text_splitter_config(self):
        return self._text_splitter_config
    

class RAGServiceContext:
    def __init__(self, config: Config = None):
        self._llm = None
        self._embedder = None
        self._text_splitter = None
        self._model_config = None
        self._service_context = None
        self._printer = PrettyPrinter(indent=4, width=40)

        if config:
            self.load_models_from_config(config)
            self._generate_service_context_from_models()
            self._model_config = config
    
    def set_llm(self, model_config: RAGServiceConfig) -> bool:
        self._llm = model_config.llm_class(**model_config.llm_config.params)

    def set_embedder(self, model_config: Config) -> bool:
        self._embedder = model_config.embedder_class(
            **model_config.embedder_config.params)

    def set_text_splitter(self, model_config: Config) -> bool:
        self._text_splitter = model_config.text_splitter_class(
            **model_config.text_splitter_config.params)

    def load_models_from_config(self, config: RAGServiceConfig):
        if not self._model_config:
            self._model_config = config
        # LLM
        self.set_llm(model_config=config)
        self.set_embedder(model_config=config)
        self.set_text_splitter(model_config=config)
        
    def _generate_service_context_from_models(self):
        # Service Context wrapping LLM
        self._service_context = ServiceContext.from_defaults(
            llm=self._llm, embed_model=self._embedder, 
            text_splitter=self._text_splitter,)
            
    @property
    def llm(self):
        return self._llm
    
    @property
    def embedder(self):
        return self._embedder
    
    @property
    def text_splitter(self):
        return self._text_splitter
    
    @property
    def service_context(self):
        return self._service_context
    
    @property
    def model_config(self):
        return self._model_config
