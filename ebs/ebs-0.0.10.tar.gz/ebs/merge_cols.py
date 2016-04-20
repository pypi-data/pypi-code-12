"""Merges two dfs, preserving original order


Keyword arguments:
in_df       -- the dataframe that should have a column added
new_data_df -- the dataframe containg the data to add
in_col      -- int with the col to merge on in in_df
new_col     -- int with the col to merge on in new_data_df
"""

def attach_data(in_df, new_data_df, in_col, new_col):

    # if names, not indices, convert to idx
    in_col = _colname_to_idx(in_df.columns, in_col)
    new_col = _colname_to_idx(new_data_df.columns, new_col)

    # hack to ensure that when the marge col in both dfs have same name
    # the second one can safely be removed afterwards
    new_data_df.rename(columns={new_data_df.columns[new_col]:
                                'merge_on_and_then_drop_me'}, inplace=True)


    relevant_new_data = _get_relevant_new_data(in_df, new_data_df, in_col,
                                               new_col)

    in_col_name = in_df.columns[in_col]
    new_col_name = new_data_df.columns[new_col]

    # storing original sort order as datacol to get sort order back after merge
    in_df = in_df.reset_index()

    merged_df = in_df.merge(relevant_new_data, left_on=in_col_name,
                            right_on=new_col_name, how="left", sort=False)

    merged_df = _post_merge_cleanup(merged_df, new_col_name)

    return merged_df


def _colname_to_idx(df_columns, col):

    try:
        col = int(col)
    except ValueError:
        df_columns = list(df_columns)
        _check_no_duplicates(df_columns)
        col = df_columns.index(col)

    return col

def _check_no_duplicates(df_columns):

    assert len(df_columns) == len(set(df_columns)), \
        "Input df contains duplicates: {}".format(", ".join(df_columns))

def _get_relevant_new_data(in_df, new_data_df, in_col, new_col):

    in_data_merge_col = in_df.iloc[:, in_col]
    new_data_merge_col = new_data_df.iloc[:, new_col]

    relevant_rows_from_new_data_df = new_data_merge_col.isin(in_data_merge_col)
    relevant_new_data = new_data_df[relevant_rows_from_new_data_df]

    return relevant_new_data


def _post_merge_cleanup(in_df, new_col_name):

    """Drops col we merged on and gets pre-merge sort order back"""

    in_df = in_df.drop(new_col_name, axis=1)

    pre_merge_sort_order_col = list(in_df.columns)[0]
    in_df = in_df.sort_values(pre_merge_sort_order_col)
    in_df = in_df.drop(pre_merge_sort_order_col, axis=1)

    return in_df
