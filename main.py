"privremeni main fajl koji sluzi za testiranje registracije plug-ina"

from core.plugin_registry import PluginRegistry


def main():

    registry = PluginRegistry()

    # Discover all available plugins
    registry.discover_plugins()

    # Print discovered visualizers
    print("VISUALIZER PLUGINS:")

    for name, plugin in registry.get_visualizers().items():
        print(f"- {name}")

    # Print discovered data sources
    print("\nDATA SOURCE PLUGINS:")

    for name, plugin in registry.get_data_sources().items():
        print(f"- {name}")


if __name__ == "__main__":
    main()