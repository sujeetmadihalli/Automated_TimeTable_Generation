import pandas as pd
import webbrowser as wb

periods = ['9:30 - 10:30', 
'10:30 - 11:30',
'11:30 - 12:30',
'12:30 - 1:30', 
'2:30 - 3:30',
'3:30 - 4:30',
'4:30 - 5:30']

days = ['Mon','Tue','Wed','Thu','Fri','Sat']

#data is dictionary
def generate_xlsx(data):
    
    for section in data['sections']:
        for div in data['divs']:
            df = pd.DataFrame(index=days, columns=periods)
            for i in range(len(data['schedule'])):
                if data['schedule'][i].section == section.section_id and data['schedule'][i].room == div:
                    
                    df[data['schedule'][i].time][data['schedule'][i].day] = str(data['schedule'][i].course) + " by Prof. " + str(data['schedule'][i].instructor)
            
            df.to_excel(f'..\OUTPUTS\EXCEL\{section.section_id}_{div}.xlsx')
            df.to_html(f'..\OUTPUTS\HTML\{section.section_id}_{div}.html')
            wb.open_new_tab(f'..\OUTPUTS\HTML\{section.section_id}_{div}.html')
  
