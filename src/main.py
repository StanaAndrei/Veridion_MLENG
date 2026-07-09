import click

@click.command()
@click.option(
    '--ifile', '-i',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Input file(jsonl format)'
)
@click.option('--query', prompt='Query', help='Query input')
def main(ifile, query):
    print("Hello World")
    print(f'Query {query} on {ifile}')

if __name__ == '__main__':
    main()