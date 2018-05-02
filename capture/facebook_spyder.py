# -*- coding: utf-8 -*-

import json
import html as htmlentities
import sys
import traceback
import scrapy
from lxml import html, etree
from friend_pagination_request import FriendPaginationRequest
from pymongo import MongoClient
from pymongo import ReturnDocument

MUTUAL = 3
ALL = 2

END_FRIENDS_CAPTURE = 0
CONTINUE_FRIENDS_CAPTURE = 1

NUMERO_MAXIMO_AMIGOS = 5000

class FacebookSpyder(scrapy.Spider):
    name = "Facebook"
    username = ""
    profile_id = ""
    profile = ""
    collection = ""
    controle = {}
    genders = 0
    friends = {}
    pagelet_token = ""
    lst = ""

    client = MongoClient('localhost', 27017)
    db = client.facebook

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'LOG_LEVEL': 'INFO'
    }

    url = 'https://www.facebook.com/'
    start_urls = [
        url
    ]
    
    def parse(self, response):
        access = open("access")
        lines = access.readlines()
        email = lines[0]
        passw = lines[1]
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email': email, 'pass': passw},
            callback=self.after_login
        )

    def after_login(self, response):
        html = response.text
        try:
            comeco = html.index('viewerid') + 10
        except ValueError:
            self.logger.error("Login falhou!")
        self.logger.info("Login efetuado com sucesso")
        id = html[comeco:comeco+20]
        self.profile_id = id[0:id.index("\"")]
        try:
            fim = html.index("\" title=\"Perfil\"")
        except ValueError:
            fim = html.index("\" title=\"Profile\"")
        profile = html[fim-100:fim]
        antes_perfil = "facebook.com/"
        self.profile = profile[profile.index(antes_perfil)+len(antes_perfil):len(profile)]
        self.logger.info("id:{}, profile:{}".format(self.profile_id, self.profile))
        return scrapy.Request(self.url+self.profile, callback=self.get_friends_page_link)

    def handle_page(self, response):
        page = ""
        for code in response.xpath('//code'):
            div = code.extract()
            inicio = div.index("<!-- ")+5
            fim = div.index(" -->")
            page += div[inicio:fim]
        return html.fromstring(page)

    def get_friends_page_link(self, response):
        tree = self.handle_page(response)
        friends_page_url = tree.xpath(".//a[@data-tab-key='friends']/@href")[0]
        self.logger.info(friends_page_url)
        return scrapy.Request(friends_page_url, callback=self.get_others_user_info)

    def find_something(self, start, end, lenght, string, include_start=False):
        comeco = string.index(start)
        saida = string[comeco:comeco+lenght]
        if include_start:
            comeco = 0
        else:
            comeco = len(start)
        fim = saida.index(end)
        return saida[comeco:fim]

    def get_others_user_info(self, response):    
        friends_page = response.text
        self.collection_wrapper = self.find_something("collection_wrapper_", '" class', 100, friends_page)
        self.pagelet_token = self.find_something('pagelet_token:"', '",', 100, friends_page)
        self.lst = self.find_something(',lst:"', '"}', 60, friends_page)

        self.username = response.xpath(".//title/text()").extract()[0]
        self.user_collection = self.db[self.username]
        self.logger.info("username: "+self.username)
        self.logger.info("collection: "+self.collection_wrapper)
        self.logger.info("pagelet_token: "+self.pagelet_token)
        self.logger.info("lst: "+self.lst)
        return self.start_collect_friends()
        
    def start_collect_friends(self):
        self.controle['counter'] = 0
        self.controle['friend_profile_id'] = self.profile_id
        self.controle['collection_wrapper'] = self.collection_wrapper
        self.controle['colecao'] = ALL
        self.controle['cursor'] = ""
        self.controle['pagelet_token'] = self.pagelet_token
        self.controle['lst'] = self.lst
        self.controle['my_profile_id'] = self.profile_id
        self.friends = {}
        self.links = {}
        self.controle['requests'] = 0

        request = FriendPaginationRequest(self.profile_id, 
                                          self.collection_wrapper, 
                                          ALL, 
                                          "", 
                                          self.profile_id, 
                                          self.pagelet_token,
                                          self.lst)

        self.logger.info("Coletando amigos de "+self.username)

        url = request.get_request()
        friends_pagination_request = scrapy.Request(url, callback=self.handle_friends_pagination)
        #self.logger.info("Request: {}".format(url))
        friends_pagination_request.meta['request'] = request
        return friends_pagination_request

    def handle_friends_pagination(self, response):
        friends_page = response.text
        request = response.meta['request']

        try:
            # Buscando a chave para a próxima paginação de amigos
            cursor = self.find_something('MDpub3Rfc3R', '"', 100, friends_page, True)

            # Apagando o 'for (;;);' do começo da página
            # Decodificando entidades HTML ex.: &quot; &amp;
            # Fazendo o parsing do JSON
            json_data = json.loads(friends_page[len('for (;;);'):len(friends_page)])
            #self.logger.info(json_data["payload"])
            
            # Pegando o elemento dentro do JSON que contém a página
            is_continue = CONTINUE_FRIENDS_CAPTURE
            try:
                if json_data["payload"] != "":
                    friends_page_tree = html.fromstring(htmlentities.unescape(json_data["payload"]))
                else:
                    is_continue = END_FRIENDS_CAPTURE    
            except etree.XMLSyntaxError:
                self.logger.info("Captura de amigos finalizada")
                is_continue = END_FRIENDS_CAPTURE

            #"".decode('unicode_escape')
            #"".encode('utf-8'))
        except ValueError:
            self.logger.info("Captura interrompida")
            is_continue = END_FRIENDS_CAPTURE

        # Analisando a próxima página
        if is_continue != END_FRIENDS_CAPTURE:
            if request.colecao == ALL:
                is_continue = self.get_friends(friends_page_tree)
            else:
                friend_profile_id = request.friend_profile_id
                self.is_mutual_friend_collected(friends_page_tree, friend_profile_id)
                is_continue = CONTINUE_FRIENDS_CAPTURE

        if is_continue != END_FRIENDS_CAPTURE:
            #url = self.get_friends_pagination_request(controle)
            request.cursor = cursor
            newUrl = request.get_request()
            #self.logger.info("Request: {}".format(newUrl))
            friends_pagination_request = scrapy.Request(newUrl, callback=self.handle_friends_pagination)
            friends_pagination_request.meta['request'] = request
            yield friends_pagination_request
        else:
            self.controle['colecao'] = MUTUAL
            for gender_capture in self.start_genders_capture():
                yield gender_capture
            for status_capture in self.start_statuses_capture():
                yield status_capture
            for links_capture in self.get_links():
                yield links_capture

    def get_friends(self, friends_node_page):

        # Pegando a div que contém todas as informações do amigo e iterando para cada um
        for div_friends in friends_node_page.xpath(".//div[@data-testid='friend_list_item']"):

            # Pegando id do profile do amigo
            profile_id = div_friends.xpath('.//button[contains(@data-flloc, "profile_browser")]/@data-profileid')[0]

            # Pegando o profile do amigo
            profile = div_friends.xpath('.//div[@class="uiProfileBlockContent"]//a')[0]
            profile = profile.attrib["href"]
            try:
                profile = profile[profile.index('.com/')+5:len(profile)]
            except ValueError:
                # Não faz nada (perfis desabilitados não possuem links)
                pass

            if "profile" not in profile:
                if "?" in profile:
                    profile = profile[0:profile.index("?")] 
            else:
                if "&" in profile:
                    profile = profile[0:profile.index("&")]

            # Pegando o link para a imagem do amigo
            img = div_friends.xpath('.//img/@src')[0]

            # Pegando todos os links dentro dessa div
            links = div_friends.xpath('.//a')
            n_links = len(links)
            # Pegando o nome
            try:
                if n_links == 4:
                    nome = str(links[2].xpath('text()')[0])
                else:
                    nome = str(links[1].xpath('text()')[0])
            except IndexError:
                continue

            self.controle['counter'] += 1
            friend = {"counter": self.controle['counter'], 
                      "name": nome, 
                      "userName": profile, 
                      "id": profile_id, 
                      "image": img}

            #self.logger.info(friend)

            #exit()
            
            self.user_collection.insert_one(friend)

            self.logger.info("Usuário {} salvo".format(friend['name']))

            # Adicionando amigo na lista de ids
            self.friends[profile_id] = friend

            # Parando o programa ao coletar a quantidade de amigos desejada
            if self.controle['counter'] >= NUMERO_MAXIMO_AMIGOS:
                return END_FRIENDS_CAPTURE

        return CONTINUE_FRIENDS_CAPTURE

    def is_mutual_friend_collected(self, friends_node_page, friend_profile_id):
        for div_friends in friends_node_page.xpath(".//div[@data-pnref='mutual']"):

            # Pegando id do perfil do amigo mútuo
            profile_id = div_friends.xpath('.//button[contains(@data-flloc, "profile_browser")]/@data-profileid')[0]

            try:
                if self.friends[profile_id]:
                    self.logger.info("#Mutual: {} eh amig@ de {}".format(self.friends[friend_profile_id]["name"], self.friends[profile_id]["name"]))
                    self.user_collection.find_one_and_update({"id": profile_id}, {'$push': {'links': friend_profile_id}}, return_document=ReturnDocument.AFTER)
            except:
                pass

    def start_genders_capture(self):
        for profile_id, friend in self.friends.items():
            if friend["userName"] == "#": # Perfis Inativos
                continue
            url = "https://www.facebook.com/{}/about?section=contact-info&pnref=about".format(friend["userName"])
            if "profile" in friend["userName"]:
                url = "https://www.facebook.com/profile.php?id={}&sk=about&section=contact-info&pnref=about".format(profile_id) 
            request = scrapy.Request(url, callback=self.set_gender)
            request.meta['profile_id'] = profile_id
            yield request

    def set_gender(self, response):
        tree = self.handle_page(response)
        profile_id = response.meta['profile_id']
        gender_div = tree.xpath('//span[text()="Gender"]/../../div')
        friend = self.friends[profile_id]
        if len(gender_div) == 0:
            gender_div = tree.xpath('//span[text()="Gênero"]/../../div')
        if (len(gender_div) != 0):
            gender = str(etree.tostring(gender_div[1], method="text", encoding='UTF-8'), 'utf-8')
            self.logger.info("#Genero: {} eh do sexo {}".format(friend["name"], gender))
            self.user_collection.find_one_and_update({"id": profile_id}, {'$set': {'genero': gender}}, return_document=ReturnDocument.AFTER)

    def start_statuses_capture(self):
        for profile_id, friend in self.friends.items():
            if friend["userName"] == "#": # Perfis Inativos
                continue
            url = "https://www.facebook.com/{}/about?section=relationship".format(friend["userName"])
            if "profile" in friend["userName"]:
                url = "https://www.facebook.com/profile.php?id={}%2Fabout%3F&sk=about&section=relationship&pnref=about".format(profile_id) 
            request = scrapy.Request(url, callback=self.set_status)
            request.meta['profile_id'] = profile_id
            yield request

    def set_status(self, response):
        tree = self.handle_page(response)
        profile_id = response.meta['profile_id']
        status_ul = tree.xpath(".//ul[contains(@class,'fbProfileEditExperiences')]")[0]
        status = str(etree.tostring(status_ul, method="text", encoding='UTF-8'), 'utf-8')
        if status == 'Nenhuma informação de relacionamento a ser exibida' or status == "No relationship info to show":
            status = "-"
        friend = self.friends[profile_id]
        #friend["status"] = status
        self.logger.info("#Status: {} está {}".format(friend["name"],status))
        #self.user_collection.replace_one({"id": profile_id}, friend, True)
        self.user_collection.find_one_and_update({"id": profile_id}, {'$set': {'status': status}}, return_document=ReturnDocument.AFTER)


    def get_links(self):
        self.controle["links"] = 0
        for profile_id, _ in self.friends.items():
            url = 'https://www.facebook.com/{}/friends_mutual'.format(profile_id)
            friends_pagination_request = scrapy.Request(url, callback=self.get_mutual_friends)
            friends_pagination_request.meta['friend_profile_id'] = profile_id
            yield friends_pagination_request

    def get_mutual_friends(self, response):

        friends_page = response.text

        #file = io.open('test.html', mode='w', encoding='utf-8')
        #file.write(friends_page)
        #file.close()
        
        friend_id = response.meta['friend_profile_id']

        try:
            collection_wrapper = self.find_something("collection_wrapper_", '" class', 100, friends_page)
            pagelet_token = self.find_something('pagelet_token:"', '"}', 100, friends_page)
            lst = self.find_something(',lst:"', '"}', 60, friends_page)
            friend_request = FriendPaginationRequest(self.controle['my_profile_id'], 
                                                     collection_wrapper, 
                                                     MUTUAL, 
                                                     "", 
                                                     friend_id, 
                                                     pagelet_token, 
                                                     lst)
            url = friend_request.get_request()

            self.logger.info("Verificando amigos mútuos de: " + self.friends[friend_id]["name"])

            request = scrapy.Request(url,callback=self.handle_friends_pagination)
            request.meta['request'] = friend_request
            return request
        except ValueError:
            self.logger.info("## Pagina indisponivel de: " + self.friends[friend_id]["name"])
