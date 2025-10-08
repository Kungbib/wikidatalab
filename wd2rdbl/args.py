def get_args():
    import argparse

    argp = argparse.ArgumentParser()
    argp.add_argument('-o', '--output', default='trig')
    argp.add_argument('-na', '--nest-annotations', action='store_true', default=False)
    argp.add_argument('-nq', '--nest-quoted', action='store_true', default=False)
    argp.add_argument('sources', metavar='SOURCE', nargs='*')

    return argp.parse_args()
