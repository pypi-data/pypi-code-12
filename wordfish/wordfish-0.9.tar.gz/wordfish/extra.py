# Create a matrix of labels, keep track of which abstracts are labeled
labels = pandas.DataFrame(columns=term_names)

for r in range(len(meta)):
    meta_file = meta[r]
    text = meta_file.replace("_meta","_sentences")
    label = os.path.basename(text).split("_")[0]
    # Build a model for everyone else
    if label not in vectors.index:
        try:
            print "Processing %s of %s" %(r,len(meta))
            vectors.loc[label] = analyzer.text2mean_vector(text)
            labels.loc[label,read_json(meta_file)["labels"]] = 1
        except:
            pass

