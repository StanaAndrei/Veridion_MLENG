import click
from hamilton import driver
from pipe_stages import read, query_parser, hard_filter, semantic_filter, answer
from Types.Qualification import FinalQualificationReport


@click.command()
@click.option(
    '--infile', '-i',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Input file (jsonl format)'
)
@click.option('--query', prompt='Query', help='Query input')
def main(infile: str, query: str):
    click.echo("Initializing hybrid match framework...")

    dr = (
        driver.Builder()
        .with_modules(read, query_parser, hard_filter, semantic_filter, answer)
        .build()
    )

    inputs = {
        "infile": infile,
        "query": query
    }

    results = dr.execute(
        final_vars=["final_count", "filtered_count", "final_evaluation"],
        inputs=inputs
    )

    initial_count = results["final_count"]
    post_filter_count = results["filtered_count"]
    report: FinalQualificationReport = results["final_evaluation"]

    click.echo("\n==============================================")
    click.echo(f"Original Query: '{query}'")
    click.echo(f"Total Companies Evaluated: {initial_count}")
    click.echo(f"Surviving Hard Filters: {post_filter_count}")
    click.echo("==============================================\n")

    click.echo("--- Final Qualified Results from LLM Judge ---")

    true_matches = [m for m in report.qualified_matches if m.is_true_match]

    if not true_matches:
        click.echo("⚠ No valid companies in the dataset satisfied your specific query constraints.")
        if report.qualified_matches:
            click.echo("\n(Closest candidates evaluated and rejected by the judge:)")
            for match in report.qualified_matches[:3]:
                click.echo(f"  - {match.operational_name}: {match.justification}")
    else:
        for match in true_matches:
            click.echo(f"[✓ MATCH] {match.operational_name} (Conf: {match.confidence_score})")
            click.echo(f"   Reason: {match.justification}\n")

    click.echo("==============================================\n")


if __name__ == '__main__':
    main()