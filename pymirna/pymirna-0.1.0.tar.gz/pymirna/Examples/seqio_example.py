import sys

from pymirna.SeqIO.fastaReader import FastaReader

def main(dataset_filename):
    fasta = FastaReader(dataset_filename)
    print(fasta.getID())
    print(fasta.getSequence())
    while(not fasta.isEOF()):
        fasta.nextSequence()
        print(fasta.getID())
        print(fasta.getSequence())

if __name__=="__main__":
    main(sys.argv[1])  # read input filename from 1st command-line argument
