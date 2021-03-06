def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, required=True, help="launcher config path."
    )

    args = parser.parse_args()

    launcher_config_path = args.config
    controller = Controller(launcher_config_path)

    controller.setup_logging()
    controller.setup_root()

    LOG.info("Execution started.")
    controller.execute_root()
    LOG.info("Execution completed.")


if __name__ == "__main__":
    import argparse
    import logging
    from core.controller import Controller

    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger(__name__)

    LOG.info("Setting up prerequisites...")
    main()
