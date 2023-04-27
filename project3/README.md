# CS6111: Project 3
## Names and Unis
Ryan Grossmann (rg3398)

Matthew Bu (mb4753)

## Files
* INTEGRATED-DATASET.csv : Project Dataset
* main.py : python script to run apriori algorithm
* example_run.txt : output of compelling sample run

## How to Run
* `python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>`

## Dataset
* We used two datasets:
    * 2006 - 2011 NYS Math Test Results By Grade - School Level - All Students
    * 2006 - 2012 School Demographics and Accountability Snapshot
* To generate the dataset:
    * Math Results:
        * Eliminated any row where Grade != 'All Grades"
        * Eliminated columns: 
            * Grade
            * Category
            * Number Tested
            * Mean Scale Score
            * Level 1 #
            * Level 2 #
            * Level 3 #
            * Level 4 #
            * Level 3+4 #
    * Demographics:
        * Removed all rows where schoolyear == '20112012'
        * Changed every schoolyear value to its corresponding year, changed schoolyear to Year
            * 20052006 -> 2005
            * 20062007 -> 2006
            * 20072008 -> 2007
            * 20082009 -> 2008
            * 20092010 -> 2009
            * 20102011 -> 2010
        * Removed all columns except:
            * DBN
            * Year (changed from schoolyear)
            * ell_percent
            * sped_percent
            * asian_per
            * black_per
            * hispanic_per
            * white_per
* The datasets were joined on DBN and Year, then these columns were removed
* These datasets together can provide some insight into the correlation between demographics and test scores for students in grades 3-8.

## Internal Design
We implemented the basic apriori algorithm but tweaked the data processing that gets fed into the main association rule function. Specifically, we had to find a way to group data since most of the items we were working with were percentages. Consequently, in our first trials, we would see association rules with specific complementary percentages (for example {male 59%}={female 41%}) which were accurate, but do not provide any real meaningful value. As a result, through trial and error, we grouped our items into 'buckets', the ideal size of which we found to be groups of 20 from 0-100. Also, for readability purposes, we append the column name to their respective values so we could tell what the items mean (note this does not affect the result of the apriori algorithm since every item would lead with their respective column name).

## Sample Run Command Line
python3 main.py INTEGRATED-DATASET.csv 0.2 0.8 > example_run.txt

## Additional Information
        
