import pymysql

# input as grid list

grid_list = ['23423444','7541496', '02343444', '00111122']

def select_grid_from_infos(cursor, grid_list):
    grid_list_str = ', '.join(grid_list)
    print(grid_list_str)

    query_list = ['SELECT * FROM infos']
    query_list.append(f'WHERE grid_id IN ({grid_list_str})')

    query_str = " ".join(query_list)
    cursor.execute(query_str)

    return query_str

def select_grid_from_rooms(cursor, grid_list):
    grid_list_str = ', '.join(grid_list)
    print(grid_list_str)

    query_list = ['SELECT * FROM rooms']
    query_list.append(f'WHERE grid_id IN ({grid_list_str})')

    query_str = " ".join(query_list)
    
    cursor.execute(query_str)
    print(query_str)

    return query_str

if __name__ == '__main__':

    #pymysql.connect(host=db_config['DB_HOST'], port=int(db_config['DB_PORT']), user=db_config['DB_USER'], 
                        # passwd = db_config['DB_PASSWORD'], db =db_config['DB_NAME'], charset=db_config['DB_CHARSET'])

    db = pymysql.connect(host='localhost', port=3306, user='dalci', passwd='UpKoDah4', db='upkodah_item', charset='utf8mb4')

    cursor = db.cursor()
    print("DB connection Success")

    # get grid id

    select_grid_from_infos(cursor, grid_list)
    infos = cursor.fetchall()

    for one_info in infos:
        print(one_info)

    select_grid_from_rooms(cursor, grid_list)
    rooms = cursor.fetchall()

    for one_room in rooms:
        print(one_room)

    db.close()