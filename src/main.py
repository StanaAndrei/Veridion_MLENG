import click
from hamilton import driver
from pipe_stages import read, query_parser, hard_filter, semantic_filter, answer


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

    # Added semantic_filter stage to the active pipeline tracking definitions
    dr = (
        driver.Builder()
        .with_modules(read, query_parser, hard_filter, semantic_filter, answer)
        .build()
    )

    inputs = {
        "ifile": ifile,
        "query": query
    }

    results = dr.execute(
        final_vars=["parsed_intent", "final_count", "filtered_count", "ranked_semantic_candidates"],
        inputs=inputs
    )

    intent = results["parsed_intent"]
    initial_count = results["final_count"]
    post_filter_count = results["filtered_count"]
    ranked_pool = results["ranked_semantic_candidates"]

    click.echo("\n=== Gemini Pipeline Progress Output ===")
    click.echo(f"Original Query: '{query}'")
    click.echo(f"Total Dataset Count: {initial_count}")
    click.echo(f"Surviving Hard Filters: {post_filter_count}")
    click.echo(f"Semantic Funnel Output Count: {len(ranked_pool)}")

    if ranked_pool:
        click.echo("\n--- Top Semantically Ranked Candidates ---")
        for idx, comp in enumerate(ranked_pool[:3], 1):
            click.echo(f"{idx}. {comp.operational_name} (Geo: {comp.address.country_code if comp.address else '??'})")
    click.echo("=========================================\n")


if __name__ == '__main__':
    main()