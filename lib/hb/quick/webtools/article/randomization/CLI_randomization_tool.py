import click

@click.command()
@click.option('-i','--inputFile',required=True, type = click.Path(), help='a BED file (or) a Gsuite file (or) a directory containing several BED files')
@click.option('-c','--chrLens', required=True, type = click.File(), help='tab-delimited text file containing chr lengths of the genome')
@click.option('-r','--restrict', type = click.File(), help='BED file (or) intensity file containing region universe to restrict the shuffling')
@click.option('-d','--distribution', default = 'anywhere', type=click.Choice(['anywhere', 'within']), help='string indicating whether shuffling should be within each chromosome or anywhere across the genome')
@click.option('-p','--preserveClumping', default = 'ignore', type=click.Choice(['ignore', 'preserve']), help='string indicating whether distances between genomic regions should be preserved')
@click.option('-a','--allowOverlaps', default = 'allow', type=click.Choice(['allow', 'disallow']), help='string indicating whether shuffled regions are allowed to overlap')
@click.option('-t','--truncateSizes', default = 'true', type=click.Choice(['true', 'false']), help='string indicating whether or not to allow truncating the sizes of shuffled regions in special cases')
@click.option('-s','--seed', type = int, help='numeric value to make the shuffling reproducible')

def permuteBed(inputfile,chrlens,restrict,distribution,preserveclumping,allowoverlaps,truncatesizes,seed):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(inputfile)
    click.echo(chrlens)
    click.echo(restrict)
    click.echo(distribution)
    click.echo(preserveclumping)
    click.echo(allowoverlaps)
    click.echo(truncatesizes)
    click.echo(seed)

if __name__ == "__main__":
    permuteBed()