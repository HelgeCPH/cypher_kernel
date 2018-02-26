## Changes between `cypher_kernel` 0.1.1 and 0.2.0

### Added parsing of lists

Cypher queries, may return lists. Examples are:

```cypher
CALL apoc.meta.graph();
```

```cypher
MATCH (n) 
RETURN labels(n) AS labels, COUNT(*) AS count
ORDER BY count DESC
```

Such lists should now be parsed correctly.


### Added support for `%%python` magic

Now, there are standard code cells, which contains Cypher code and code cells for `%%bash` and `%%python` code.

Noteable about `%%python` code cells is, that a Pandas `DataFrame` is accessible under the name `df`. It contains the results of the last Cypher query. That is, the `DataFrame` may be empty of the query did not return anything. Otherwise, it contains the data as returned by the query. Note, all contents are strings and have to be manually casted correspondingly.

For example, if a query returns:

```
+------------------------------------------------------+
| juris            | num   | officer_country           |
+------------------------------------------------------+
| "Bermuda"        | 67025 | "United States"           |
| "Aruba"          | 36191 | "Netherlands Antilles"    |
| "Bermuda"        | 12846 | "United Kingdom"          |
| "Bermuda"        | 12180 | "Hong Kong"               |
| "Cayman Islands" | 9563  | "United States"           |
| "Bermuda"        | 7818  | "Switzerland"             |
| "Aruba"          | 7168  | "Curaçao"                 |
| "Aruba"          | 5344  | "Virgin Islands, British" |
| "Bermuda"        | 4089  | "China"                   |
| "Bermuda"        | 3794  | "Canada"                  |
| "Aruba"          | 3627  | "Saint Kitts and Nevis"   |
| "Bermuda"        | 3123  | "Singapore"               |
| "Cayman Islands" | 2585  | "China"                   |
| "Bermuda"        | 2556  | "Australia"               |
| "Bermuda"        | 2219  | "British Virgin Islands"  |
| "Isle of Man"    | 2032  | "United Kingdom"          |
| "Bermuda"        | 1912  | "Cayman Islands"          |
| "Cayman Islands" | 1739  | "United Kingdom"          |
| "Bermuda"        | 1629  | "France"                  |
| "Cayman Islands" | 1596  | "Hong Kong"               |
+------------------------------------------------------+
```

The corresponding `DataFrame` looks as:

```
               juris    num            officer_country
0          "Bermuda"  67025            "United States"
1            "Aruba"  36191     "Netherlands Antilles"
2          "Bermuda"  12846           "United Kingdom"
3          "Bermuda"  12180                "Hong Kong"
4   "Cayman Islands"   9563            "United States"
5          "Bermuda"   7818              "Switzerland"
6            "Aruba"   7168                  "Curaçao"
7            "Aruba"   5344  "Virgin Islands, British"
8          "Bermuda"   4089                    "China"
9          "Bermuda"   3794                   "Canada"
10           "Aruba"   3627    "Saint Kitts and Nevis"
11         "Bermuda"   3123                "Singapore"
12  "Cayman Islands"   2585                    "China"
13         "Bermuda"   2556                "Australia"
14         "Bermuda"   2219   "British Virgin Islands"
15     "Isle of Man"   2032           "United Kingdom"
16         "Bermuda"   1912           "Cayman Islands"
17  "Cayman Islands"   1739           "United Kingdom"
18         "Bermuda"   1629                   "France"
19  "Cayman Islands"   1596                "Hong Kong"
```


### Syntax highlighting

Cypher code is now highligthed correctly. Thanks to Thomas' answer to my question on the Jupyter Help repository, see https://github.com/jupyter/help/issues/301