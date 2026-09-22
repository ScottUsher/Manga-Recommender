
import numpy as np
from sortedcontainers import SortedDict
import math
        

#**********************************************************************
# Purpose: finds the dictionaries that hold user ratings that are the same manga as the program user has rated
#
# Precondition: valid manga-first dictionary and dictionary of user ratings
#               
# Postcondition: returns dictionary of mang holding manga ratings
#
#***********************************************************************
def find_manga(manga_first: SortedDict, program_user: dict):
    searched_dict = {}
    for manga in program_user:
        searched_dict[manga] = manga_first[manga]

    return searched_dict
    # returns a dict of the list of manga to find


#**********************************************************************
# Purpose: find all of the users who have rated the selected manga and put them and those ratings into a dictionary
#
# Precondition: a valid dictionray of program user rated manga and mangafirst dictionary 
#
# Postcondition: returns a dictionary of users who have rated what the program user has
#
#***********************************************************************
def compile_ratings (manga_first: SortedDict, program_user: dict):
    rating_lists = find_manga(manga_first, program_user)
    userdict = {}
    for title, ratings in rating_lists.items():

        for user in ratings:
            compiled_user = userdict.get(user[0]) #user[0] is the key of which user the row of ratings belong to
        
            if compiled_user == None:

                userdict[user[0]] = {}
            
            userdict[user[0]][title] = user

    return userdict


#**********************************************************************
# Purpose: rank user similarity to the product user
#
# Precondition: uses compile_ratings output as user_scores, goal is the product user's rating of manga, and weights is a list of biases of which manga is more reliable
#               
#
# Postcondition: returns a dict of users with a list of scores of how similar they are to the user for each evaluation type
#
#***********************************************************************
def process_user_scores(relavent_users: dict, program_user_manga : dict, weights: dict):     

    user_similarity = {}

    for user in relavent_users: #the goal from this is to make multiple lists of evaluation types a list of product_user manga that has the same elements as the user
        weight_total = 0
        weight_difference_total = 0
        manga_overlap = 0

        for manga in program_user_manga:
            if manga in relavent_users[user]:        #this will skew the data to recomend users who agree with one show and have watched none other as very similar which is bad, however....
                                            # this skewing of data is not actually that bad but definately does exist. it skews the results to have more data make the output closer to zero on average
                                            # in effect this means the more data the better the relavence score on average, which is not necesarily bad

                manga_overlap += 1

                manga_confidence = weights[manga]

                product_user_zscore = program_user_manga[manga][1] 
                user_zscore = relavent_users[user][manga][2]

                user_difference = abs(product_user_zscore - user_zscore)

                weight_difference_total += user_difference * manga_confidence #ex: -0.0327*(2 or something)
                weight_total += manga_confidence


        if weight_total > 0:
            average_difference = weight_difference_total/weight_total
            similarity = math.exp(-average_difference)
            
        else:
            similarity = 0                     


        confidence = manga_overlap/(manga_overlap+ len(program_user_manga)+5)
        if (similarity * confidence) > 1:
            print("similarity: ",similarity, " confidence: ",confidence)

        user_similarity[int(user)] = similarity * confidence

    return user_similarity


#**********************************************************************
# Purpose: output an orderd list of shows that the user may like going from most likely to least
#
# Precondition: uses compile_ratings output as user_scores, user_dict is the user first dictionary of manga holding show scores, and manga_dict is the manga fitst dictonary of users holding show scores
#               
# Postcondition: returns a dict of manga with a score of 
#
#***********************************************************************
def suggestion_dict(user_similarity: dict, user_dict: dict, manga_dict: dict):
    posible_suggestions = {} 
    ordering_dict = {}

    for user in user_similarity:

        for manga in user_dict[user]:
            #add manga and user identifier
            if manga not in ordering_dict:
                ordering_dict[manga] = [user]
            else:
                ordering_dict[manga].append(user)

    for manga in ordering_dict: # goes through all manga that users from "user_similarity" have rated

        for user in ordering_dict[manga]:

            for i in manga_dict[manga]:
                if int(i[0]) == user: # if a user from "user_similarity" is found the rating is added to the list

                    similarity = user_similarity[i[0]]
                    user_zscore = i[2] #this line messed up a couple of days of coding, make sure you know your indicies 3 is not 2 might be close but its alway worth double checking what you are accessing
                    
                    if manga in posible_suggestions:
                        posible_suggestions[manga][user] = [similarity, user_zscore]  

                    else:
                        posible_suggestions[manga] = {}
                        posible_suggestions[manga][user] = [similarity, user_zscore]

    suggestions = {}
    for manga in posible_suggestions:


        similarity_by_z_show_total = 0
        similarity_total = 0

        for user in posible_suggestions[manga]:

            similarity_by_z_show_total += posible_suggestions[manga][user][0] * posible_suggestions[manga][user][1]
            similarity_total += posible_suggestions[manga][user][0]


        confidence = similarity_total / (similarity_total+2)

        if similarity_total == 0:
            suggestions[manga] = 0
        else:
            suggestions[manga] = ((similarity_by_z_show_total/similarity_total)*confidence) # here is where a negative modifier could be added
    
    
    return dict(sorted(suggestions.items(), key = lambda item: item[1], reverse=True))
    #return orderd_suggestions


#**********************************************************************
# Purpose: giving a z score to each program user rating of a manga
#
# Precondition: have a program user manga rating dict, have global average and standard deviation 
#               
# Postcondition: returns a dict holding both the rating and z-score of each manga
#
#***********************************************************************
def normalize_program_user(program_user : dict, global_average, global_std):
    list = []
    for manga in program_user:
        list.append(program_user[manga])

    list = np.array(list)
    std = np.std(list)
    average = np.average(list)

    program_user_info = {} 

    for manga in program_user:
        if len(program_user) > 4:
            min_std = 0.6
            program_user_info[manga] = [program_user[manga], (float((program_user[manga] - average) / max(std, min_std)))]# this is a cludge and is gross
        else:
            program_user_info[manga] = [program_user[manga], (float((program_user[manga] - global_average) / global_std))]

    
    return program_user_info


#**********************************************************************
# Purpose: finding weight of manga selected by the progarm user
#
# Precondition: valid program user manga dictionary, and manga data 
#               
# Postcondition: returns the show weight of selected manga as a dictionary of manga
#
#***********************************************************************
def find_show_weight(program_user, manga_data):
    needed_weight = {}
    for manga in program_user:
        needed_weight[manga] = manga_data[manga][0]
    return needed_weight


#**********************************************************************
# Purpose: removing manga searched by the program user from the manga sugestion list
#
# Precondition: dictonary of program user manga and computed recomendation list 
#               
# Postcondition: returns recomendation list without the manga searched by the program user
#
#***********************************************************************
def drop_reference_shows(ProgramUser, suggestions):
    for manga in ProgramUser:
        if manga in suggestions:
            suggestions.pop(manga)
    
    return suggestions
    

#**********************************************************************
# Purpose: providing a list of recomended manga based on manga rated by the program user
#
# Precondition: validd dictonary of program user manga, manga first dictionary, user first list, manga data, computed global average and global standard deviation
#               
# Postcondition: returns a list of manga recomendations based on the manga the program user rated
#
#***********************************************************************
def manga_recomendation(ProgramUser, manga_first_collection, user_first_collection, manga_data, global_average, global_std):

    weights = find_show_weight(ProgramUser, manga_data)
    user_manga = compile_ratings(manga_first_collection, ProgramUser)
    norm_prog_user = normalize_program_user(ProgramUser, global_average, global_std)
    user_similarity_scores = process_user_scores(user_manga, norm_prog_user, weights)
    suggestions = suggestion_dict(user_similarity_scores, user_first_collection, manga_first_collection)
    final_suggestions = drop_reference_shows(ProgramUser, suggestions)
    
    return final_suggestions