from bs4 import BeautifulSoup

VALID_CODE = [0]
NO_ITEM_CODE = [3,4,7,8]
ERROR_CODE = [2,5]
NEED_MORE_CODE = [1,6]

def inspect_hearder_code(bsxml):
    ''' xml BeaufitulSoup 객체를 받아서 header code 검사 '''
    hdcode = bsxml.find('headerCd')
    # fail to find 'headerCd'
    if hdcode == None:
        print("ERROR: Header Code is missing")
    elif hdcode == 0:
        print('Successful Request.')
    elif hdcode == 1:
        print('API System Error')
        # TODO: raise API System Error
    elif hdcode == 2:
        print('WrongQueryRequestError: Check your query parameters.')
        # TODO: raise WrongQueryRequestError
    elif hdcode == 3:
        print('No item: Cannot find a station.')
    elif hdcode == 4:
        print('No item: Cannot find a route.')
    elif hdcode == 5:
        print('WrongPositionInputError: Check your position input.')
        # TODO: WrongPositionInputError
    elif hdcode == 6:
        print('Cannot read the realtime information. Request after a while')
        # TODO: raise API temporary error
    elif hdcode == 7:
        print('No item: There is no path result.')
    elif hdcode == 8:
        print('End of Operation')
    else:
        pass
    return hdcode

# TODO: raise API System Error
# TODO: raise WrongQueryRequestError
# TODO: WrongPositionInputError
# TODO: raise API temporary error