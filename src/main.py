import click
from hamilton import driver
from pipe_stages import read, answer


@click.command()
@click.option(
    '--ifile', '-i',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Input file (jsonl format)'
)
@click.option('--query', prompt='Query', help='Query input')
def main(ifile: str, query: str):
    click.echo(f"Initializing baseline pipeline for query: '{query}'")

    pipeline_modules = [read, answer]
    dr = driver.Driver({}, *pipeline_modules)

    inputs = {
        "ifile": ifile
    }

    results = dr.execute(
        final_vars=["final_count"],
        inputs=inputs
    )

    raw_count = results["final_count"]

    # If Hamilton wrapped it in a Pandas Series/Dataframe, pull the underlying value
    if hasattr(raw_count, "iloc"):
        count = raw_count.iloc[0]
    elif isinstance(raw_count, dict):
        count = list(raw_count.values())[0]
    else:
        count = raw_count

    click.echo(f"Pipeline complete. Total initial candidate companies: {count}")


if __name__ == '__main__':
    main()