import asyncio
import psycopg2

async def intToSTR(summa):
    if type(summa)!=int:
        return summa
    summa_str = str(summa)
    indexi = 0
    for i in range(len(summa_str)):
        if summa_str[i]=='-':
            indexi = i
            summa_str = summa_str[i+1:]
    counter=0
    for i in range(len(summa_str), 0, -1):

        if counter>2:
            summa_str = summa_str[0:i]+','+summa_str[i:]
            counter=0
        counter += 1
    if "-" in str(summa):
        summa_str = '-'+summa_str
    return summa_str




async def set_user_lang(user_id, lang='en'):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')
    if user_id:
        sql = f"""
            SELECT bot_lang, edu_lang FROM app_students WHERE user_id = %s ;
        """
        sql_bot = f"""
            SELECT bot_lang FROM app_tguserlang WHERE user_id = %s ;
        """
        sql_update = f"""
            UPDATE app_students SET bot_lang = %s WHERE user_id = %s;
        """

        sql_create = f"""
            INSERT INTO app_tguserlang (user_id, bot_lang) VALUES (%s, %s);
        """
        curr = conn.cursor()

        curr.execute(sql, (str(user_id), )) #
        if not curr.fetchone():

            curr.execute(sql_bot, (str(user_id), )) #
            if not curr.fetchone():
                curr.execute(sql_create, (str(user_id), lang))
        else:
            curr.execute(sql_update, (lang, str(user_id))) #
        conn.commit()

    curr.close()   
    conn.close()
    return lang



async def get_user_lang(user_id=None, lang='en'):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')

    if user_id:
        sql = f"""
            SELECT bot_lang, edu_lang FROM app_students WHERE user_id = %s;
            """
    cur = conn.cursor()
    cur.execute(sql, (str(user_id), ))
    res = cur.fetchone()
    if res is None:
        cur.close()
        conn.close()
        return lang or 'en'
    cur.close()
    conn.close()
    return res[0] or res[1] or lang

async def write_to_bot_history(id, message):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')
    curr = conn.cursor()

    sql = f"""
        INSERT INTO app_bothistory (user_id, message) VALUES (%s, %s);
    """
    curr.execute(sql, (id, message))
    conn.commit()
    curr.close()
    conn.close()
    return True



async def user_datas(user_id, lang=None):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')

    if lang is None:
        lang='en'
    sql = f"""
        SELECT id,  id_raqam, fish, faculty,date_contracted, contract_soums, level  FROM app_students WHERE user_id = %s;
    """
    sql_1 = f"""
        SELECT date_paid, soums_paid FROM app_payments WHERE student_id = %s;
    """
    curr = conn.cursor()
    curr.execute(sql, (str(user_id), ))
    student_info = curr.fetchone()
    if student_info is None:
        return None
    curr.execute(sql_1, (student_info[0], ))
    paid_all = 0
    must_paid = 0
    payments = curr.fetchall()
    for res in payments:   #tuples' list
        paid_all += res[1]
    must_paid = student_info[5]-paid_all
    
    curr.close()
    conn.close()
    return student_info, payments, paid_all, must_paid
    
    

async def set_all_payments(payments, lang=None):
    text = ''
    if len(payments)==0:
        if lang=='ru':
            return 'Платежек пока нет..'
        if lang=='uz':
            return 'To\'lovlar yo\'q..'
        else: 
            return 'No payments yet..'
    for pay in payments:
        text+=f'  {pay[0]}                               {await intToSTR(pay[1])}\n'    
    return text

async def get_user_infos(user_id, lang=None):
    result_message = None
    not_found_message = '''
        ❌\nNot found your infos.
    '''
    user_data = await user_datas(user_id=user_id, lang=lang)
    if not user_data:
        return not_found_message
    if lang == 'ru':
        result_message = f'''
        ✅\nCтудент ид:{user_data[0][1]}\nФИО: {user_data[0][2]}\nФакультет: {user_data[0][3]}\nДоговор: {user_data[0][1]}  дата: {user_data[0][4]}\n\n\nContract Сумы:                       {await intToSTR(user_data[0][5])}\n\nПлатеж произведен:\n{await set_all_payments(user_data[1], lang)}\n\nПлатеж произведен:                {await intToSTR(user_data[2])}\nДолжен быть оплачен:            {await intToSTR(user_data[3])}
        '''
    
    if lang == 'en':
        result_message = f'''
        ✅\nStudent id:{user_data[0][1]}\nFull name: {user_data[0][2]}\nFaculty: {user_data[0][3]}\nContract: {user_data[0][1]}  date: {user_data[0][4]}\n\n\nContract Soums:                       {await intToSTR(user_data[0][5])}\n\nPayment made:\n{await set_all_payments(user_data[1], lang)}\n\nPayment made:                          {await intToSTR(user_data[2])}\nMust be paid:                              {await intToSTR(user_data[3])}
        '''
    if lang == 'uz':
        result_message = f'''
        ✅\nTalaba id:{user_data[0][1]}\nF.I.O: {user_data[0][2]}\nFakultet: {user_data[0][3]}\nShartnoma: {user_data[0][1]}  sana: {user_data[0][4]}\n\n\nShartnoma summasi:              {await intToSTR(user_data[0][5])}\n\nTo'lov amalga oshirildi:\n{await set_all_payments(user_data[1], lang)}\n\nTo'lov amalga oshirildi:             { await intToSTR(user_data[2])}\nTo'lanishi kerak:                          {await intToSTR(user_data[3])}
        '''
    await write_to_bot_history(user_data[0][0], message=result_message)
    return result_message or not_found_message





async def update_user_object(user_id, phone):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')
    sql_getting = f"""
        SELECT fish FROM app_students WHERE phone_number=%s;
        """
    sql = f"""
        UPDATE app_students SET bot_used=%s , user_id=%s where phone_number=%s;
        """
    cur = conn.cursor()

    cur.execute(sql_getting, (phone,))
    user = cur.fetchone()
    cur.execute(sql, (True, str(user_id), phone))
    conn.commit()
    conn.close()
    if user is not None:
        return user[0]
    return user
    
async def get_admins_contact():
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')
    admins = []
    sql = f"""
        SELECT phone_number, first_name FROM app_admins;
    """
    curr = conn.cursor()
    curr.execute(sql)
    res = curr.fetchall()
    return res

#######SYNCRONICALLY


def get_intToSTR(summa):
    if type(summa)!=int:
        return summa
    summa_str = str(summa)
    indexi = 0
    for i in range(len(summa_str)):
        if summa_str[i]=='-':
            indexi = i
            summa_str = summa_str[i+1:]
    counter=0
    for i in range(len(summa_str), 0, -1):

        if counter>2:
            summa_str = summa_str[0:i]+','+summa_str[i:]
            counter=0
        counter += 1
    if "-" in str(summa):
        summa_str = '-'+summa_str
    return summa_str
def get_all_payments(payments, lang=None):
    text = ''
    if len(payments)==0:
        if lang=='ru':
            return 'Платежек пока нет..'
        if lang=='uz':
            return 'To\'lovlar yo\'q..'
        else: 
            return 'No payments yet..'
    for pay in payments:
        text+=f'  {pay[0]}                               {get_intToSTR(pay[1])}\n'    
    return text


def sync_write_to_bot_history(id, message):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')
    curr = conn.cursor()

    sql = f"""
        INSERT INTO app_bothistory (user_id, message) VALUES (%s, %s);
    """
    curr.execute(sql, (id, message))
    conn.commit()
    curr.close()
    conn.close()
    return True



def get_user_datas(user_id, lang=None):
    conn = psycopg2.connect(database='tiue_bot', user='admin', password='testing321')

    if lang is None:
        lang='en'
    sql = f"""
        SELECT id,  id_raqam, fish, faculty,date_contracted, contract_soums, level  FROM app_students WHERE user_id = %s;
    """
    sql_1 = f"""
        SELECT date_paid, soums_paid FROM app_payments WHERE student_id = %s;
    """
    curr = conn.cursor()
    curr.execute(sql, (str(user_id), ))
    student_info = curr.fetchone()
    if student_info is None:
        return None
    curr.execute(sql_1, (student_info[0], ))
    paid_all = 0
    must_paid = 0
    payments = curr.fetchall()
    for res in payments:   #tuples' list
        paid_all += res[1]
    must_paid = student_info[5]-paid_all
    
    print("payments: ",payments)
    curr.close()
    conn.close()
    return student_info, payments, paid_all, must_paid


def get_user_infos_by_bot(user_id, lang=None):
    result_message = None
    not_found_message = '''
        ❌\nNot found your infos.
    '''
    user_data = get_user_datas(user_id=user_id, lang=lang)
    if not user_data:
        return None
    if lang == 'ru':
        result_message = f'''
        ✅\nCтудент ид:{user_data[0][1]}\nФИО: {user_data[0][2]}\nФакультет: {user_data[0][3]}\nДоговор: {user_data[0][1]}  дата: {user_data[0][4]}\n\n\nContract Сумы:                       {get_intToSTR(user_data[0][5])}\n\nПлатеж произведен:\n{get_all_payments(user_data[1], lang)}\n\nПлатеж произведен:                {get_intToSTR(user_data[2])}\nДолжен быть оплачен:            {get_intToSTR(user_data[3])}
        '''
    
    if lang == 'en':
        result_message = f'''
        ✅\nStudent id:{user_data[0][1]}\nFull name: {user_data[0][2]}\nFaculty: {user_data[0][3]}\nContract: {user_data[0][1]}  date: {user_data[0][4]}\n\n\nContract Soums:                       {get_intToSTR(user_data[0][5])}\n\nPayment made:\n{get_all_payments(user_data[1], lang)}\n\nPayment made:                          {get_intToSTR(user_data[2])}\nMust be paid:                              {get_intToSTR(user_data[3])}
        '''
    if lang == 'uz':
        result_message = f'''
        ✅\nTalaba id:{user_data[0][1]}\nF.I.O: {user_data[0][2]}\nFakultet: {user_data[0][3]}\nShartnoma: {user_data[0][1]}  sana: {user_data[0][4]}\n\n\nShartnoma summasi:              {get_intToSTR(user_data[0][5])}\n\nTo'lov amalga oshirildi:\n{get_all_payments(user_data[1], lang)}\n\nTo'lov amalga oshirildi:             { get_intToSTR(user_data[2])}\nTo'lanishi kerak:                          {get_intToSTR(user_data[3])}
        '''
    sync_write_to_bot_history(user_data[0][0], message=result_message)
    return result_message or not_found_message