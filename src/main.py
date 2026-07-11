import click
from hamilton import driver
from pipe_stages import read, query_parser, hard_filter, answer


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

    # We use the modern Hamilton Builder to construct our driver safely.
    # by default, when not using any dataframe adapters, it outputs a clean dictionary.
    dr = (
        driver.Builder()
        .with_modules(read, query_parser, hard_filter, answer)
        .build()
    )

    inputs = {
        "ifile": ifile,
        "query": query
    }

    # .execute() now returns a clean, standard Python dictionary containing your raw objects.
    results = dr.execute(
        final_vars=["parsed_intent", "final_count", "filtered_count"],
        inputs=inputs
    )

    intent = results["parsed_intent"]
    initial_count = results["final_count"]
    post_filter_count = results["filtered_count"]

    click.echo("\n=== Gemini Query Parser Output ===")
    click.echo(f"Original Query: '{query}'")
    click.echo(f"Hard Filters Geo: {intent.hard_filters.country_code}")
    click.echo(f"Total Initial Candidates: {initial_count}")
    click.echo(f"Candidates Remaining After Hard Filters: {post_filter_count}")
    click.echo("==================================\n")


if __name__ == '__main__':
    main()