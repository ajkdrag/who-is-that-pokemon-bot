PROC_TYPE_MAP = {
    "pipeline": "libs.processes.pipeline.PipelineProcess",
    "scraping": "libs.processes.scraping.ScrapingProcess",
    "preprocessing": "libs.processes.preprocessing.PreprocessingProcess",
    "training": "libs.processes.training.TrainingProcess",
    "inferencing": "libs.processes.inferencing.InferencingProcess",
}

SCRAPING_TYPE_MAP = {"pokemondb": "libs.scrapers.pokemondb.PokemonDB"}

PREPROCESSING_TYPE_MAP = {
    "silhouette": "libs.preprocessors.silhouette.Silhouette",
    "augmentation": "libs.preprocessors.augmentation.Augmentation",
}

TRAINING_TYPE_MAP = {"train": "libs.training.train.Train"}

SERVICE_TYPE_MAP = {
    "server": "libs.services.inference_server.Server",
    "bot": "libs.services.bot_client.Bot",
}
