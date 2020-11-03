print("Hi welcome to Corona Informer")
print("Choose the following option to run that ")
print("1. Mask Detection\n2. Corona cases of a country\n3. Self assessment of corona\n4. Information about vaccine\n5. prevention tips\n6. Comparision of cases of two country")
user=int(input("Enter option number you want to perform:- "))
if user==1:
    import cv2
    import sys
    import winsound
    freq=500
    dur=100

    cascPath = sys.argv[1]
    mouthCascade = cv2.CascadeClassifier(cascPath)

    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        mouth = mouthCascade.detectMultiScale(gray, 1.3, 5)
    # Draw a rectangle around the faces
        for (x, y, w, h) in mouth:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            winsound.Beep(freq, dur) 

    
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
elif user==2:
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    READ_FROM_URL = True
    LOCAL_CSV_FILE = 'covid-19-cases.csv'
    MIN_CASES = 100
    count=input("Enter country name for present covid-19 cases.   Note please enter first letter capital :- ")
    country = count
    data_loc = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/'
               'csse_covid_19_data/csse_covid_19_time_series'
               '/time_series_covid19_confirmed_global.csv')
    if not READ_FROM_URL:
        data_loc = LOCAL_CSV_FILE
    df = pd.read_csv(data_loc)
    grouped = df.groupby('Country/Region')
    df2 = grouped.sum()
    c_df = df2.loc[country, df2.columns[3:]]
    # Discard any columns with fewer than MIN_CASES.
    c_df = c_df[c_df >= MIN_CASES].astype(int)
    # Convet index to a proper datetime object
    c_df.index = pd.to_datetime(c_df.index)
    n = len(c_df)
    if n == 0:
        print('Too few data to plot: minimum number of cases is {}'
                .format(MIN_CASES))
        sys.exit(1)
    fig = plt.Figure()
    ax2 = plt.subplot2grid((4,1), (0,0))
    ax1 = plt.subplot2grid((4,1), (1,0), rowspan=3)
    ax1.bar(range(n), c_df.values)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    c_df_change = c_df.diff()
    ax2.plot(range(n), c_df_change.values)
    ax2.set_xticks([])
    ax1.set_xlabel('Days since {} cases'.format(MIN_CASES))
    ax1.set_ylabel('Confirmed cases, $N$')
    ax2.set_ylabel('$\Delta N$')
    title = '{}\n{} cases on {}'.format(country, c_df[-1],
                c_df.index[-1].strftime('%d %B %Y'))
    plt.suptitle(title)
    plt.show()
    
    
elif user==3:
    q1="Are you currently experiencing any of these issues? 1. Serve difficulty in breathing 2. Serve chest pain 3. Feeling confused or unsure of where you are  4. Losing consciousness  :-  "
    score=0
    q2="Have you been contact with person suffering covid-19 in past 14 days   :-   "
    mistake=0
    q3="In the last 48 hours, have you had any of the following NEW symptoms? 1. Fever of 100 F (37.8 C) or above  2. Cough  3. Sore throat  4. Loss of smell or taste, or a change in taste   :-   "

    print("WELCOME TO SELF CHECK OF CORONA VIRUS ")
    print("PLEASE ENTER THE INFORMATION CORRECT ")
    name = input("PLEASE  ENTER YOUR NAME ")
    age =int(input("PLEASE ENTER YOUR AGE "))
    if age<=130:
        print("WE ARE GOING TO START YOUR TEST PLEASE ENTER 1 FOR YES AND 2 FOR NO ")
        a1=int(input(q1))
        if a1==1:
            score=1
        elif a1==0:
            score=0
        else:
            print("You have enter wrong detail please only enter 1 for yes and 2 for no")
            mistake=1
    
    
        a2=int(input(q2))
        if a2==1:
            score+=1
        elif a2==0:
            score+=0
        else:
            print("You have enter wrong detail again you will not be able to contunue ")
            mistake+=1
        
        if mistake==0:
            a3=int(input(q3))
            if a3==1:
                score+=1
            elif a3==0:
                score+=0
            else:
                print("please enter correct details ")
            
            
            if score==3:
                print("Your rate of risk is very high  please check your corona test")
        
            elif score==2:
                print("your rate of risk is moderate")
        
            elif score==1:
                print("your rate of risk is low")
    
            elif score==0:
                print("your rate of risk is very low") 
        print("Thanks for taking the test ")
    
    else:
        print("Thanks for becoming a part of us your age is above the limit")
        
        
        
        
elif user==4:
    import pandas as pd
    a=['Ad5-nCoV','Recombinant vaccine(adenovirus type 5 vector)','CanSino Biologics','Phase 3','Tongji Hospital, Wuhan, China']
    b=['AZD1222','Replication-deficient viral vector vaccine (adenovirus from chimpanzees)','The University of Oxford; AstraZeneca; IQVIA; Serum Institute of India','Phase 3','The University of Oxford, the Jenner Institute']
    c=['CoronaVac','Inactivated vaccine (formalin with alum adjuvant)','Sinovac','Phase 3','Sinovac Research and Development Co., Ltd.']
    d=['JNJ-78436735 (formerly Ad26.COV2-S)','Non-replicating viral vector','Johnson & Johnson','Phase 3','Johnson & Johnson']
    e=['mRNA-1273','mRNA-based vaccine','Moderna','Phase 3','Kaiser Permanente Washington Health Research Institute']
    f=['No name announced','Inactivated vaccine','Wuhan Institute of Biological Products; China National Pharmaceutical Group (Sinopharm)','Phase 3','Henan Provincial Center for Disease Control and Prevention']
    g=['NVX-CoV2373','Nanoparticle vaccine','Novavax','Phase 3','Novavax']
    h=['Bacillus Calmette-Guerin (BCG) vaccine','Live-attenuated vaccine','University of Melbourne and Murdoch Children’s Research Institute; Radboud University Medical Center; Faustman Lab at Massachusetts General Hospital','Phase 2/3','University of Melbourne and Murdoch Children’s Research Institute; Radboud University Medical Center; Faustman Lab at Massachusetts General Hospital']
    i=['BNT162','mRNA-based vaccine','Pfizer, BioNTech','Phase 2/3','Multiple study sites in Europe and North America']
    j=['Covaxin','Inactivated vaccine','Bharat Biotech; National Institute of Virology','Phase 2','']

    df = pd.DataFrame([a,b,c,d,e,f,g,h,i,j],['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th'],['Name','Mechanism','Sponsor','Trial Phase','Instituion'])
    print(df)
    
    
elif user==5:
    import time
    print("Here are some that we should follow to prevent us from getting infected:-")
    time.sleep(3)
    print("")
    print("")

    print("Clean your hands often")
    time.sleep(2)
    print("")
    print("")
    print("Cough or sneeze in your bent elbow - not your hands!")
    time.sleep(3)
    print("")
    print("")
    print("Avoid touching your eyes, nose and mouth")
    time.sleep(2)
    print("")
    print("")
    print("Limit social gatherings and time spent in crowded places.")
    time.sleep(3)
    print("")
    print("")
    print("Avoid close contact with someone who is sick.")
    time.sleep(2)
    print("")
    print("")
    print("Clean and disinfect frequently touched objects and surfaces.")
    time.sleep(3)
    print("")
    print("")
    print("Here were some tips to prevent yourself from getting infected ")
    time.sleep(2)
    print("")
    print("")
    print("For more information please visit to link given below:-")
    time.sleep(2)
    print("https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public?gclid=Cj0KCQjwxNT8BRD9ARIsAJ8S5xbnBH6vnMLAppeWLw0c-KLq6o_IXhuSo6W8H8ZxzMQTd_-QZ36U4BQaAkFBEALw_wcB")
    time.sleep(1)
    print("")
    print("")
    print("Thanks for being our part")
    
    
elif user==6:
    # importing all tkinter files
    from tkinter import *
    from covid import Covid
    from  matplotlib import pyplot as plt
    # create instance of tkinter
    root = Tk()
   # setting geometry of tkinter window
    root.geometry("450x450")
# setting title of tkinter window
    root.title("CORONAVIRUS (COVID-19) UPDATE")

# defining the function to fetch the data from covid library and to show it.
    def covid_data():
    # importing matplotlib which will be used to show data graphically
        from matplotlib import pyplot as plt
    # to scale the data we are importing patches
        import matplotlib.patches as mpatches
    # importing covid library
        from covid import Covid
    # initializing covid library
        covid = Covid()
    # this declares empty lists to store different data sets
        cases = []
        confirmed = []
        active = []
        deaths = []
        recovered = []
       # using Exception Handling to handle the exceptions.
        try:
        # updating root(tkinter window)
            root.update()
        # getting countries names entered by the user using get() method.
            countries = data.get()
        # removing white spaces from the start and end of the string
            country_names = countries.strip()
        # replacing white spaces with commas inside the string
            country_names = country_names.replace(" ", ",")
        # splitting the string to store names of countries
        # as a list
            country_names = country_names.split(",")
        # for loop to get all countries data
            for x in country_names:
            # appending countries data one-by-one in cases list
            # here, the data will be stored as a dictionary
            # for one country i.e. for each country
            # there will be one dictionary in the list
            # which will contain the whole information
            # of that country
                cases.append(covid.get_status_by_country_name(x))
            # updating the root
                root.update()
        # for loop to get one country data stored as dict in list cases
            for y in cases:
            # storing every Country's confirmed cases in the confirmed list
                confirmed.append(y["confirmed"])
            # storing every Country's active cases in the active list
                active.append(y["active"])
            # storing every Country's deaths cases in the deaths list
                deaths.append(y["deaths"])
            # storing every Country's recovered cases in the recovered list
                recovered.append(y["recovered"])
        # marking the color information on scaleusing patches
            confirmed_patch = mpatches.Patch(color='blue', label='Confirmed')
            recovered_patch = mpatches.Patch(color='green', label='Recovered')
            active_patch = mpatches.Patch(color='red', label='Active')
            deaths_patch = mpatches.Patch(color='black', label='Deaths')
        # plotting the scale on graph using legend()
            plt.legend(handles=[confirmed_patch, recovered_patch, active_patch, deaths_patch])
        # showing the data using graphs
            for x in range(len(country_names)):
                plt.bar(country_names[x], confirmed[x], color='blue')
                if recovered[x] > active[x]:
                    plt.bar(country_names[x], recovered[x], color='green')
                    plt.bar(country_names[x], active[x], color='red')
                else:
                    plt.bar(country_names[x], active[x], color='red')
                    plt.bar(country_names[x], recovered[x], color='green')
                plt.bar(country_names[x], deaths[x], color='black')
        # setting the title of the graph
            plt.title('CURRENT COVID CASES')
        # giving label to x direction of graph
            plt.xlabel('COUNTRY NAME')
        # giving label to y direction of graph
            plt.ylabel('CASES(in millions)')
        # showing the full graph
            plt.show()
        except Exception as e:
        # the user must enter the correct details during entering the country names
        # otherwise, they will enter into this section
        # so ask them to diffrentiate the names using comma or space but not both.

            data.set("Enter the correct details please:")


    Label(root, text="COVID-19 UPDATES\nEnter the countries names\nfor whom you want to get the\ncovid-19 data", font="LUCIDA 15 bold").pack()
    Label(root, text="Enter the Country Names seperated by coma").pack()
    data = StringVar() #creating instance of StringVar()
#setting the text that will be displayed by default on GUI application. 
    data.set("")
#Entry widget is used to accepts the string text from the user.
    entry = Entry(root, textvariable=data, width=50).pack()
 #here Button widget is used to create a button that will call the function "covid_data"
#created above when any on-CLICK event will occur.
    Button(root, text="Get Data", command=covid_data).pack()
#this helps to run the mainloop
    root.mainloop()
    
    
else:
    print("Sorry your option is invalid please check it")
