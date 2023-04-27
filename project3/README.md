# CS6111: Project 3
## Names and Unis
Ryan Grossmann (rg3398)

Matthew Bu (mb4753)

## Files
* INTEGRATED-DATASET.csv : Project Dataset
* main.py : python script to run apriori algorithm
* requirements.txt : all dependencies used

## How to Run
* `pip3 install -r requirements.txt`
* `python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>`

## Dataset
* We used three datasets:
    * 2006 - 2011 NYS Math Test Results By Grade - School Level - All Students
    * 2005-2010 Graduation Outcomes - School Level
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
    * Graduation Outcomes:
        * Eliminated any row where Demographic != 'Total Cohort'
        * Eliminated any row where Total Grads n == 's'
        * Changed every Cohort value to its corresponding year, changed Cohort to Year
            * 2001 -> 2005
            * 2002 -> 2006
            * 2003 -> 2007
            * 2004 -> 2008
            * 2005 -> 2009
            * 2006 Aug -> 2010
        * Removed all columns except:
            * DBN
            * Year (changed from Cohort)
            * Total Grads - % of Cohort
            * Still Enrolled - % of Cohort
            * Dropped Out - % of Cohort
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
            * total_enrollment
            * ell_percent
            * sped_percent
            * asian_per
            * black_per
            * hispanic_per
            * white_per
            * male_per
            * female_per
* All three datasets were joined on DBN and Year
* These datasets together can provide some insight into how certain schools and school demographics affect test scores for students in grades 3-8 and graduation rates for high schoolers. These datasets can also shed light on which years had higher or lower test scores and graduation rates.

## Internal Design
We implemented the basic apriori algorithm but tweaked the data processing that gets fed into the main association rule function. Specifically, we had to find a way to group data since most of the items we were working with were percentages. Consequently, in our first trials, we would see association rules with specific complementary percentages (for example {male 59%}={female 41%}) which were accurate, but do not provide any real meaningful value. As a result, through trial and error, we grouped our items into 'buckets', the ideal size of which we found to be groups of 20 from 0-100. Also, for readability purposes, we append the column name to their respective values so we could tell what the items mean (note this does not affect the result of the apriori algorithm since every item would lead with their respective column name).

## Sample Run Command Line
python3 main.py INTEGRATED-DATASET.csv 0.2 0.8 > output.txt

## Additional Information
        
