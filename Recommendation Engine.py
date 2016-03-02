
# coding: utf-8

# # Building A Simple Recommendation Engine With Python

# A recommendation engine is a great tool when searching for suggestions on a personal basis. In other words, the search results are tailored to the tastes of the user rather than some hard-coded attribute in the results (i.e. date created, keywords, synonyms, location). 
# 
# One example of a recommendation is collaborative filtering. This method uses the historical preferences of a large group of other people to make a decision for you. One example is how Amazon displays similar books: people who liked book A and B also liked book C. Therefore, because you behaved similar to group X in that you liked book A and B, it is not a far leap to assume that you will also like book C. 

# This ipython notebook shows a python example that is adapted from "Programming Collective Intelligence: Building Smart Web 2.0 Applications." You can follow along here if you would like: http://it-ebooks.info/book/330/

# Before we can give suggestions, we will need a history of preferences. This example shows how seven users felt about 6 movies: Lady in the Water, Snakes on a Plane, Just My Luck, Superman Returns, You, Me and Dupree, and The Night Listener. This is shown below:

# In[ ]:

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


# Now that we have the historical data, we will now need to map out the similarities/differences in our group X. To this, we can calculate the distance between person A and person B based on either the Euclidean distance or Pearson correlation. The euclidean distance is essentially the distance of person A or B to the X/Y axis (with the axis being sort of like the ground truth).

# Because we have so many people (5), we're not going to go one by one and calculate the distances for everyone. We are going to create a function and a loop to save us the effort. 

# In[18]:

def sim_distance(prefs, p1, p2):
    '''
    Returns a distance-based similarity score for person1 and person2.
    '''

    # Get the list of shared_items
    si = {}
    for movie in prefs[p1]:
        if movie in prefs[p2]:
            si[movie] = 1
    # If they have no ratings in common, return 0
    if len(si) == 0:
        return 0
        # Add up the squares of all the differences
        sum_of_squares = sum([pow(prefs[p1][movie] - prefs[p2][movie], 2) for movie in
                         prefs[p1] if movie in prefs[p2]])
    return 1 / (1 + sum_of_squares)


# **note Programming Collective Intelligence used "item" instead of "movie" in this function. I felt movie would be more helpful for the reader** Here "prefs" refers to our "critics" array shown earlier which has the a) user and b) ratings for three movies. p1 and p2 refer to two users. si = {} means a list of our shared items. We've defined function. Now lets give it a whirl. 

# In[19]:

sim_distance(critics, 'Lisa Rose', 'Gene Seymour')


# To recap what just happened, we inputed our "prefs" array and two users Lisa and Gene. We essentially did a loop to calculate the sum_of_squares between Lisa and Gene for a particular movie going to every single movie. 

# In[ ]:

sum_of_squares = sum([pow(prefs[p1][movie] - prefs[p2][movie], 2) for movie in
                         prefs[p1] if movie in prefs[p2]])


# I'm going to create a one_of_squares just to show how one iteration looks like: sum([pow(critics['Lisa Rose']['Lady in the Water'] - critics['Gene Seymour']['Lady in the Water'],2)])

# In[25]:

one_of_squares = sum([pow(critics['Lisa Rose']['Lady in the Water'] - critics['Gene Seymour']['Lady in the Water'], 2)])


# In[26]:

one_of_squares


# Using the Euclidean distance tends not to fit well in data that has not been normalized (i.e. pretty much all data). In other words, if Lisa's definition of a bad film is a 4 and Gene's definition of a good film is a 4, it's clear Lisa's ratings will tend to scew high or for Gene, vice versa. An alternative method is to use a Pearson score. For simplicity, you can read about this further in 'Programming Collective Intelligence'. 

# Now that we are able to understand the similarities between two people, we can now introduce an external agent (i.e. another user) and see how they compare. 

# In[35]:

def topMatches(
    prefs,
    person,
    n=5,
    similarity=sim_distance,
):
    '''
    Returns the best matches for person from the prefs dictionary. 
    Number of results and similarity function are optional params.
    '''

    scores = [(similarity(prefs, person, other), other) for other in prefs
              if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


# To get the "top matches" score, we are going to call our sim_distance function we already made earlier for "other" person. In this case, that "other" will be 'Toby.' "n" will be how many scores we want to display. 

# In[37]:

topMatches(critics,'Toby', n=5)


# Toby is most similar to Mick and least similar to Jack. 

# To find and sort our similarities with other users is one thing. And in some cases, it could be useful in a lot of applications. For example, what if you are a project manager and want to group employees based on their tastes of particular projects? Can you think of any other grouping applications? 
# 
# To create a recommendation engine involves an extra step (i.e. we don't want to know our similarities with other employees, we want to know what other projects we should work on based on other employees' preference on projects). 
# 
# To do this, we will create a function called 'getRecommendations.'

# In[52]:

def getRecommendations(prefs, person, similarity=sim_distance):
    '''
    Gets recommendations for a person by using a weighted average
    of every other user's rankings
    '''

    totals = {}
    simSums = {}
    for other in prefs:
    # Don't compare me to myself
        if other == person:
            continue
        sim = similarity(prefs, person, other)
    # Ignore scores of zero or lower
    for item in prefs[other]:
        # Only score movies I haven't seen yet
        if item not in prefs[person] or prefs[person][item] == 0:
            # Similarity * Score
            totals.setdefault(item, 0)
            # The final score is calculated by multiplying each item by the
            #   similarity and adding these products together
            totals[item] += prefs[other][item] * sim
            # Sum of similarities
            simSums.setdefault(item, 0)
            simSums[item] += sim
    # Create the normalized list
    rankings = [(total / simSums[item], item) for (item, total) in
                totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings


# The for loop goes through every other person in our critics dictionary and calculates how similar they are to the person specified. In our case, we are that specified person - 'toby.' Let's give it a whirl. We are 'toby' and as you can see, we've only reviewed three movies and have no idea what other movies we may like.

# In[53]:

getRecommendations(critics,'Toby', similarity=sim_distance)


# Not only did we get a great idea of what movies we may like. But, we also got a prediction of what our rating of these movies would be. We would moderately like the 'The Night Listener' and not like the 'Lady in the Water' (based on the experiences of the other movie watchers.

# ...and that's it we've built our first recommendation engine. Feel free to try it using your own dictionary at the beginning of this tutorial. You can also import a .csv and watch how much better the recommender may perform when the reviews scale.

# In[ ]:



