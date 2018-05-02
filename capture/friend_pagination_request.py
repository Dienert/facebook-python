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
        request = 'https://www.facebook.com/ajax/pagelet/generic.php/AllFriendsAppCollectionPagelet?dpr=1&data=%7B%22collection_token%22%3A%22{}%3A{}%3A{}%22%2C%22cursor%22%3A%22{}%22%2C%22disablepager%22%3Afalse%2C%22overview%22%3Afalse%2C%22profile_id%22%3A%22{}%22%2C%22pagelet_token%22%3A%22{}%22%2C%22tab_key%22%3A%22friends%22%2C%22lst%22%3A%22{}%22%2C%22ftid%22%3Anull%2C%22order%22%3Anull%2C%22sk%22%3A%22friends%22%2C%22importer_state%22%3Anull%7D&__user={}&__a=1&__dyn=7AgNe-4amaxx2u6aJGeFxqeCwDKEyGgS8zQC-C267Uqzob4q2i5U4e8wywZDxtu9xK5WAx-uUuKewzAxaFQ3uaUS2SVFEgUC745Kuifz8nxm3i2y9Azo9ohwo-7-i4F9oqx-Euxm4E6qum2S2G68y2O4rGUpxy5Urx13QWwgFojgmKbyEky8-nyETwICxC4ebyaGf-Egy9EhxO2qcyWUybAUhyo8fiAxqt5ojo8V4iaxa9BK6o-4Kl1Sax25eq2l29aGucxWcyS&__req=3o&__be=1&__pc=PHASED:DEFAULT&__rev=3870282&__spin_r=3870282&__spin_b=trunk&__spin_t=1525285473'.format(self.friend_profile_id,
                                    self.collection_wrapper, 
                                    self.colecao, 
                                    self.cursor,
                                    self.friend_profile_id,
                                    self.pagelet_token,
                                    self.lst,
                                    self.my_profile_id)
        return request