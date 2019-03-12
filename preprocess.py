import json
import os
import csv
import re
import string
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from os import listdir
from os.path import isfile, join

#nltk.download('wordnet')		#if wordnet is not initially downloaded
#nltk.download('stopwords')		#if stopwords is not present initially
#nltk.download('punkt')			#if punkt is not present initially

stop_words = set(stopwords.words('english')) 

lemmatizer = WordNetLemmatizer()

act_list = []
#with open('/home/satyx/opensoft_patel_hall/Data/act.txt') as f:
 #   for row in f:
  #      act_list.append(row.lower().rstrip('\n'))
        
with open('/home/satyx/opensoft_patel_hall/Data/actlist.txt') as f:
    for row in f:
        act_list.append(row.lower().rstrip('\n'))

act_list = list(set(act_list))



def extraction(file_adr='/home/satyx/opensoft_patel_hall/Data/All_FT/2000_U_166.txt'):
    data = []
    with open('/home/satyx/opensoft_patel_hall/Data/All_FT/'+file_adr) as fl:
        for row in fl:
            data.append(row.rstrip('\n'))
    return data



def JudgeName(data):
    if'the judgment was delivered by' not in data[5].lower():
        return None

    return (data[5].strip()).lstrip('The Judgment was delivered by : ')


def Date(data):
    if re.findall(r'\d',data[3]) == []:
        return None
    return data[3].strip()

def ActCitation(data):
    all_acts_division = []
    possible_act_citation = []
    for para in data[6:-1]:
        para = para.replace(',','')
        act_containing_part = re.split(r' Act \d+',para)
        all_acts_division.append(act_containing_part)
    
    for acts_in_para in all_acts_division:
        for acts in acts_in_para[:-1]:
            if 'the' in acts:
                possible_act_citation.append(acts.split(' the ')[-1].lower())
                
    possible_act_citation = list(set(possible_act_citation))
    act_citation = []
            
    for a in possible_act_citation:
        for act in act_list:
            if a in act:
                act_citation.append(a)
                break
    return act_citation
    
def CaseCitation(data):
    case_id= []
    z=[]
    for row in data:
        if 'indlaw' in row.lower():
            ##print(row.lower())
            z = re.findall(r'\d+ indlaw sc \d+',row.lower())
            #z = row.lower().split(' indlaw sc ')[1:]

            #for k in z:
            #   xyz = re.findall(r'\d+',k.split()[0])[0]

            case_id.extend(z)
        #break
    return case_id
            

def Judgement(data):
    return data[-1]
    


def getlist(path):
    case_docs=[f for f in listdir(path)]
    return case_docs
    
def preprocess(a):
    a=a.lower()
    word_tokens = word_tokenize(a)
    filtered_sentence = [w for w in word_tokens if not w in stop_words and w not in string.punctuation]
    lemmatised=[lemmatizer.lemmatize(w) for w in filtered_sentence]
    return lemmatised
    
        
def keywords():
    case_doc_list=getlist("/home/satyx/opensoft_patel_hall/Data/All_FT/")
    freq_dict_list=[]
    global_dict={}
    global_dict_indi={}
    cnt=0
    for i in case_doc_list[:]:
        cnt+=1
        if cnt%1000==0:
            print(cnt)
            
        if cnt==1005:
            break
        path=os.path.join("/home/satyx/opensoft_patel_hall/Data/All_FT/",i)
        fp=open(path,'r+')
        a=fp.read()
        processed_list=preprocess(a)
        freq_dict={}
        for i in processed_list:
            if i not in freq_dict.keys():
                freq_dict[i]=1
                if i not in global_dict_indi.keys():
                    global_dict_indi[i]=1
                else:
                    global_dict_indi[i]+=1
            else:
                freq_dict[i]+=1
            if i not in global_dict.keys():
                global_dict[i]=1
            else:
                global_dict[i]+=1
        freq_dict_list.append(freq_dict)

    sorted_global_dict= sorted(global_dict.items(),key=lambda x:x[1],reverse=True)
    sorted_global_dict_indi=sorted(global_dict_indi.items(),key=lambda x:x[1],reverse=True)

    sorted_global_dict
    with open("global_dict.csv","w",newline="") as f:  # open("output.csv","wb") for Python 2
        cw = csv.writer(f)
        cw.writerows(r for r in sorted_global_dict)    

    with open("global_dict_indi.csv","w",newline="") as f:  # open("output.csv","wb") for Python 2
        cw = csv.writer(f)
        cw.writerows(r for r in sorted_global_dict_indi)
        
    new_stopwords=list(stop_words)
    for x in sorted_global_dict_indi:
        if x[1]>14000:
            new_stopwords.append(x[0])
            
    new_stopwords=set(new_stopwords)
    with open("new_stopwords.csv","w",newline="") as f:  # open("output.csv","wb") for Python 2
        cw = csv.writer(f)
        cw.writerow(new_stopwords)
        
    new_dict_list=[]

    cnt=0
    for freq_dict in freq_dict_list:
        cnt+=1
        if cnt%1000 ==0:
            print(cnt)
        new_dict={}
        for x in freq_dict.keys():
            if x not in new_stopwords:
                new_dict[x]=freq_dict[x]
        new_dict_list.append(new_dict)
        
    sorted_dict=[]
    for dicti in new_dict_list:
        new_dict=sorted(dicti.items(),key=lambda x:x[1],reverse=True)
        sorted_dict.append(new_dict)
        
    docwise_keyword_list=[]
    for lists,filename in zip(sorted_dict,case_doc_list):
        cnt=0
        new_list=[]
        for x in lists:
            cnt+=1
            if cnt>30:
                break
            new_list.append(x[0])
        docwise_keyword_list.append((filename,new_list))
        
    ##print(docwise_keyword_list)                          
    
def filenames():
    path='/home/satyx/opensoft_patel_hall/Data/All_FT'
    File = os.listdir(path)
    return File



def case_id_fun():
    file = open('doc_path_ttl_id.txt', encoding="utf8")
    case_id_arr = []
    for line in file:
        line_arr = line.split("-->")
        case_id = line_arr[2].strip()
        case_id_arr.append(case_id)
    ##print(case_id_arr)


def catchwords_subject():
    file = open('/home/satyx/opensoft_patel_hall/Data/subject_keywords.txt', encoding="utf8")
    subject_arr = []
    catchwords_arr = []
    for line in file:
        line_arr = line.split("-->")
        subject_catchwords = line_arr[2].strip().split("$$$")
        subject = subject_catchwords[0]
        try:
            catchwords = subject_catchwords[1]
        except:
            catchwords = ""
        subject_arr.append(subject)
        catchwords_arr.append(catchwords)
    #print(subject_arr)
    #print(catchwords_arr)


def title(data):
    return data[0]
    """list_of_all_files = os.listdir("/home/satyx/opensoft_patel_hall/Data/All_FT")
    title_arr = []
    for files in list_of_all_files[:10]:
        with open("/home/satyx/opensoft_patel_hall/Data/All_FT/"+files) as fl:
            for line in fl:
                title_arr.append(line.rstrip('\n'))
                break
    #print(title_arr)"""

##print('Judge Name:',JudgeName())
##print('Date:',Date())
##print('Act Citation:',ActCitation())
##print('Case Citation:',CaseCitation())
##print('Judgement:',Judgement())



sub_catch={}
with open('/home/satyx/opensoft_patel_hall/Data/subject_keywords.txt') as file_r:
#with open('subject_keywords.csv','w') as file_w:

    #writer = csv.writer(file_w)
    for row in file_r:
        if '-->' not in row:
            continue
        x = row.split('-->')
        x = [i.strip() for i in x]
        y = x[-1]
        if '$$$' in y:
            y = y.split('$$$')
            x[-1] = y[-2]
            x.append(y[-1])
        else:
            x.append('')
        sub_catch[x[0]+'.txt']={'Sub':x[-3],'Cat':x[-1]}
##print(sub_catch)

"""def sub_cat(file_name):
    for i in sub_catch:
        if i[0].lower() in file_name[:-4].lower()
            return i"""


##print(sub_catch)  
df = pd.read_csv('/home/satyx/opensoft_patel_hall/Keywords_list_formatted.csv',header=None) 
df.columns = [str(i) for i in range(31)]       
def keywords_from_csv(file_name):
    meta_data = df.loc[df.loc[:,'0']==file_name].values.tolist()
    if len(meta_data)!=0:
        return meta_data[0][1:]
    return []
     
 
       
list_of_all_files = os.listdir("/home/satyx/opensoft_patel_hall/Data/All_FT")
length = len(list_of_all_files)
count =0


case = {}
with open('/home/satyx/opensoft_patel_hall/Data/doc_path_ttl_id.txt') as ids:
    for row in ids:
        if '-->' in row:
            #print('yes')
            id_case = row.split('-->')
            #print(id_case)
            id_case = [i.strip() for i in id_case]
            case[id_case[0]] = id_case[2]
            


output={}
with open('meta_data1.json','w') as file_p:
    files = os.listdir('/home/satyx/opensoft_patel_hall/Data/All_FT')
    for File in files[:5]:
        subject = ""
        catch = ""
        
        data = extraction(File)
        sub_id = {}
        with open('/home/satyx/opensoft_patel_hall/Data/doc_path_ttl_id.txt','r') as xyz:
            for row in xyz:
                line  = row.split("-->")
                line  = [ i.strip() for i in line]
                sub_id[line[0]] ={'Subject':line[1],'ID':line[2]} 
        
        df = pd.read_csv('/home/satyx/opensoft_patel_hall/Keywords_list_formatted.csv',header=None)
        df.columns = [str(i) for i in range(31)]
        
        df.loc[df.loc[:,'0']==File].values.tolist()
        
        
        keywords = keywords_from_csv(File)
        
        
        
        catch = sub_catch[File]['Cat']
        catch = catch.split(',')
        catch = [i.strip() for i in catch]
        
        catch_dash = []
        
        for i in catch:
            if i.isdigit() == False:
                catch_dash.append(i)
            else:
                catch_dash[-1] = catch_dash[-1]+','+i
        
        output[File] = {"Title": title(data), "Case ID":sub_id[File[:-4]]['ID'] , "Date": Date(data), "Judge Name": JudgeName(data), "Judgement": Judgement(data), "Case Citation":CaseCitation(data) , "Act Citaton": ActCitation(data), "Keywords": keywords_from_csv(File), "Catch":catch_dash,"Subject":sub_catch[File]['Sub']}
        
    json.dump(output,file_p)        

        
        

#data = extraction('/home/satyx/opensoft_patel_hall/Data/All_FT/2008_S_1291.txt')
##print(CaseCitation(data))
