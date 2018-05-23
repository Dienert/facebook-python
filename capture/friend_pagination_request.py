class FriendPaginationRequest:
    """Facilitador de geração de urls de paginação de amigos"""

    def __init__(self, my_profile_id, collection_wrapper, colecao, cursor, friend_profile_id, pagelet_token, lst):
        self.my_profile_id = my_profile_id
        self.collection_wrapper = collection_wrapper
        self.colecao = colecao
        self.cursor = cursor
        self.friend_profile_id = friend_profile_id
        self.pagelet_token = pagelet_token
        self.lst = lst

    def get_request(self):
        request = 'https://www.facebook.com/ajax/pagelet/generic.php/AllFriendsAppCollectionPagelet?dpr=1&data=%7B%22collection_token%22%3A%22{}%3A{}%3A{}%22%2C%22cursor%22%3A%22{}%22%2C%22disablepager%22%3Afalse%2C%22overview%22%3Afalse%2C%22profile_id%22%3A%22{}%22%2C%22pagelet_token%22%3A%22{}%22%2C%22tab_key%22%3A%22friends%22%2C%22lst%22%3A%22{}%22%2C%22ftid%22%3Anull%2C%22order%22%3Anull%2C%22sk%22%3A%22friends%22%2C%22importer_state%22%3Anull%7D&__user={}&__a=1&__dyn=7AgNe-4amaxx2u6aJGeFxqeCwDKFbGAdy8Z9LFwxx-6ES2N6wAxu13y862u9zlUC6UnGi7VXyEjKewzAxaFQ3uaUS2SVFEgUC745Kuifz8nxm1DKewBx61zUvV8iABxG7WxW5oixG1bDBwJwGxy2Su4rGUogoxu6UggZeE4am4Q5HyUG58yfDyETwICxC4ebyaGf-Egy9EhxO2qcG8HhUKjx69wwZai5FQlxdy8qAh8GcByprxCfxbCxSax2ucVEix929aGucAxCcySah4aDyequU&__req=3j&__be=1&__pc=PHASED:DEFAULT&__rev=3929140&__spin_r=3929140&__spin_b=trunk&__spin_t=1526962180'.format(self.friend_profile_id,
                                    self.collection_wrapper, 
                                    self.colecao, 
                                    self.cursor,
                                    self.friend_profile_id,
                                    self.pagelet_token,
                                    self.lst,
                                    self.my_profile_id)
        return request