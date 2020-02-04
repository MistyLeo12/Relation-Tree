# Relation-Tree

## About
While ancestral humans existed millions of years ago, modern humans have “only” been around for 200,000 some years. Modern civilization itself is only around 6000 years old. That would bring us to 4000 BC, which we already consider so long ago. In the years since then, the world’s population has exploded from an estimated 7 million to 7.5 billion.1 Due to the nature of human reproduction, it stands to reason that these 7.5 billion came from those 7 million. Not enough information is known of the earliest humans to be able to definitely say that every two people are related when we go far back enough, but we can get close, especially if we consider people with ancestors originating from the same geographical location. Perhaps the only thing that stands in our way is the lack of complete records going back far enough. And yet, if we look in the right place, there exist records that do go back far - enough being the word in question.

## Modes:
- MODE 1: Input two people and find out how they are related, if there is a known relation
- MODE 2: Input one person, and find out relatives with a certain relation to them
- MODE 3: Input two people, and get the path of their relationship between them, if any, illustrated with a visual representation of that relationship.

## Methods

### Formatting the Dataset
Makes extensive use of hashing to reduce runtime so that lookups of nodes are constant time. We read in our data from a formatted CSV file created from a converted GEDCOM file, the filetype often used to store large amounts of genealogical data. In the conversion process, each individual is assigned a unique ID. This csv file is read once and used to create a dictionary of unique IDs (type string) to values (type list) consisting of other identifying information, such as gender, birth year, mother ID, father ID, etc. Before any more advanced algorithmic calculations can be done, the initial dictionary must be cleaned. Some errors include 1) mothers being recorded as male and/or fathers being recorded as female, 2) roots (users without parents) being given “phantom-parents” - parents with IDs but no names, 3) commas in names, which is an issue due to the nature of CSV files.


### General Methods
The following methods mentioned are used in every mode because we must have a way of tracing previous generations of members such that we might find the intersection between two peoples’ lineages.  The method buildPrevGen uses the cleaned data table to make a number of lists. Each list represents a generation. To accomplish this, buildPrevGen simply starts with one list of one element -- the person whose lineage is being traced -- and all of that person’s direct ancestors are then added to the second list.  So, the second list will have the second generation of individuals.  This iteration continues until there is not enough data to go back further generations; thus we will have built a person’s entire direct ancestry.
The second of our general methods, buildNextGen2, is similar to buildPrevGen, but it creates lists of children rather than lists of parents.  The difficulties associated with this method, as opposed to buildPrevGen, have to do with the way that the original GEDCOM file was formatted.  Detailed descriptions of both of these methods follow.

### buildPrevGen(data, ret) summary
param data is a cleaned dictionary of unique IDs (a string) to identifying information (list of strings)
param ret is a list of lists
This function modifies ret with each call. It takes the last element (a list) of ret and appends a new list to ret populated with the parents (mother, then father, if any) of each person in that last list. Parent IDs are directly fetchable from data, data[id][6] is mother ID and data[id][8] is father ID. id will be found by iterating through the ids in the last element of ret. When there are no more ancestors in a generation, ret will append [0].

### buildNextGen2(data, ret) summary
param data is a dictionary of unique IDs (strings) to children IDs (list of strings). This dictionary was created from a result of a call to child_dic(dict) *defined later*, which itself inputs a cleaned dictionary, so it is by definition already cleaned. param ret is a list of lists
 
## Explanation of Mode 1 - How two people are related
Once the user has successfully given the program two ids (call these id1 and id2) to work with (detailed in the beginning of this section), a while loop is employed that calls buildPrevGen() on both users, until something in common is found on the collapsed version of the respective rets. Where collapsed() has the following effect on ret:
ret = [[A], [B, C, D, E], [F, G, H, I, J]]
collapsed(ret) = [A, B, C, D, E, F, G, H, I, J]
That was the aforementioned reason why the end of an individual’s line was indicated with a [0]; so that if id1 and id2 have no ancestors in common, that they eventually do have [0] in common, and if it is found that the only thing they have in common after termination is [0], then we can easily return that lack of relation to the user. When ancestor ids in common are found, the program finds out where in the respective rets the common id(s) were found (thus the expanding structure of ret) to determine in which generation for the two ids the ancestor belonged. This can yield three different types of relations: direct (parent, x - times great grandparent, child, x - times great - grandchild where x is between 0 and n), aunt/uncle/niece/nephew, and cousin.
This method will always guarantee closest connection(s).  Since the complete generation is built before checking for intersection, that guarantees that connections with equal strength of relation will all be found. That means that if id1 and id2 are 4th cousins in two ways, then both of those two ways will be found.
Defining the relationship and comparing strengths of relationships - an example
Estelle of Sweden’s ID is NF3FI, and Savannah Anne Kathleen Phillips’s ID is P695V. 

## Explanation of Mode 2 - Information about one person
In mode 2, termination doesn’t happen upon common ancestor but rather on user input, i.e. if the user asks for an individual’s 3x great-grandparents, then buildPrevGen() will be called until the individual’s 3x great-grandparents are found, i.e. 5 times. Mode 2 is apt to print out lots of data, i.e. in the case where the user asks for all of a person’s descendants, so this mode associates individuals with years to make printing more readable, sorting them by birth year. 


## Testing
Since the data involved is based on real individuals, it is very easy to verify correctness. In particular, we made sure to test situations where:
1)     Name matches more than one unique ID
2)     At least two types of relationships
3)     More than one closest relationship
4)     Half relationship beyond sibling - should only have one common ancestor in that branch
5)     Bad input is given
6)     People who have both full and half siblings should differentiate between the types


## Runtime

Results indicate that the algorithm is robust against scalability issues. There seems to be a linear relationship between the number of data entries processed and the runtime of our algorithm. As the results below indicate, for the greatest generational difference (7x), which was between Brian Landes and Jacob Landes, it took less than 0.05 seconds to calculate the most common ancestor between the two individuals and return their relationship. Mode 2 (calculating the pathway) takes more time as it is necessary to go through the entire tree and calculate the sum of the pathways between the two individuals all the way to completion. Of all the possible pathways, if the shortest pathway(s) (and the pathway(s) that are returned) have x generations, but the other pathways have (x + i) generations, where i > 0, the algorithm will still calculate up to (x + i) generations for each pathway. Therefore, it is easy to see how this will become a problem when we begin to venture into hundreds and thousands of pathways. As such, mode 2 scales less efficiently than mode 1.


## Future

1. Create a radial tree to visualize the family tree instead of the typical family tree visualization.
2. Find a laarger data set. 

