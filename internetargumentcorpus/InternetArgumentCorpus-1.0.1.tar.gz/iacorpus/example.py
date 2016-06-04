from iacorpus import load_dataset

def iterate_example():
    dataset = load_dataset('fourforums')
    print(dataset.dataset_metadata)
    for discussion in dataset:
        print(discussion)
        for post in discussion:
            print(post)
            exit()


if __name__ == '__main__':
    iterate_example()
