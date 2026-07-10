import click
from hamilton import driver
from pipe_stages import read, query_parser, answer


@click.command()
@click.option(
    '--ifile', '-i',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Input file (jsonl format)'
)
@click.option('--query', prompt='Query', help='Query input')
def main(ifile: str, query: str):
    click.echo("Initializing hybrid match framework...")

    # We load only the modules we want to parse
    pipeline_modules = [read, query_parser, answer]
    dr = driver.Driver({}, *pipeline_modules)

    inputs = {
        "ifile": ifile,
        "query": query
    }

    # We pull the underlying dictionary structure from Hamilton's raw node execution trace
    # to completely bypass any Pandas or Tuple type conversions.
    raw_graph_results = dr.raw_execute(
        final_vars=["parsed_intent", "final_count"],
        inputs=inputs
    )

    intent = raw_graph_results["parsed_intent"]
    count = raw_graph_results["final_count"]

    click.echo("\n=== Gemini Query Parser Output ===")
    click.echo(f"Original Query: '{query}'")
    click.echo(f"Hard Filters Geo: {intent.hard_filters.country_code}")
    click.echo(f"Hard Filters Public status: {intent.hard_filters.is_public}")
    click.echo(f"Industry primary keywords: {intent.industry_intent.primary_keywords}")
    click.echo(f"Optimized Semantic Vector Target: '{intent.semantic_search_prompt}'")
    click.echo(f"Total Initial Candidates: {count}")
    click.echo("==================================\n")


if __name__ == '__main__':
    main()