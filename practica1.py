#!/usr/bin/python3

import webapp
import csv
from urllib.parse import unquote
import os.path


class contentApp (webapp.webApp):

    urlReales = {}  # Las claves son las URLs reales
    urlCortas = {}  # Las claves son las URLs ya acortadas

    def parse(self, request):
        return (request.split(' ', 1)[0], request.split(' ', 2)[1],
                request.split('=')[-1])

    def process(self, parsed):
        method, resourceName, content = parsed
        if os.path.isfile('listaURLs.csv'):
            with open('listaURLs.csv', 'r') as fich:
                read = csv.reader(fich)
                for row in read:
                    self.urlCortas[row[0]] = row[1]
                    self.urlReales[row[1]] = row[0]
            self.contadorUrls = len(self.urlReales)
        else:
            self.contadorUrls = 0
        formulario = ("<form method = 'POST'>" +
                      "Introduce la URL que quieres acortar: " +
                      "<input type='text' name='url'><br>" +
                      "<input type='submit' value='Enviar'></form>")
        if method == "GET":
            if resourceName == "/favicon.ico":
                httpCode = "HTTP/1.1 404 Not Found"
                htmlBody = "<html><body><h1>Not Found</h1></body></html>"
            elif resourceName == "/":
                httpCode = "HTTP/1.1 200 OK"
                htmlBody = ("<html><body>" + formulario +
                            str(self.urlCortas) + "</body></html>")
            else:
                resourceName = resourceName[1:]
                if resourceName in self.urlCortas:
                    httpCode = "HTTP/1.1 302 Found"
                    htmlBody = ("<html><body><meta http-equiv='refresh'" +
                                "content='1 url=" +
                                self.urlCortas[resourceName] + "'>" +
                                "</p>" + "</body></html>")
                else:
                    httpCode = "HTTP/1.1 404 Not Found"
                    htmlBody = ("<html><body>" +
                                "Recurso no disponible.</body></html>")
        elif method == "POST":
            if content == "":
                httpCode = "HTTP/1.1 400 Bad Request"
                htmlBody = ("<html><body>" +
                            "Se ha dejado el formulario vacío.</body></html>")
            else:
                if (content[0:14] == "https%3A%2F%2F" or
                        content[0:13] == "http%3A%2F%2F"):
                    content = unquote(content)
                else:
                    content = "http://" + content
                if content in self.urlReales:
                    enlace = self.urlReales[content]
                    enlace = "http://localhost:1234/" + enlace
                    httpCode = "HTTP/1.1 200 Ok"
                    htmlBody = ("<html><body>" + "<a href=" + enlace + ">" +
                                enlace + "</a>" + "</body></html>")
                else:
                    self.urlReales[content] = self.contadorUrls
                    enlace = "http://localhost:1234/" + str(self.contadorUrls)
                    self.urlCortas[self.contadorUrls] = content
                    self.contadorUrls = self.contadorUrls + 1
                    with open('listaURLs.csv', 'w', newline='') as fich:
                        salida = csv.writer(fich)
                        for element in self.urlCortas:
                            salida.writerow([element, self.urlCortas[element]])
                    httpCode = "HTTP/1.1 200 Ok"
                    htmlBody = ("<html><body>" + "<a href=" + enlace + ">" +
                                enlace + "</a>" + "</body></html>")
        else:
            httpCode = "HTTP/1.1 405 Method Not Allowed"
            htmlBody = "Metodo distinto de POST o GET."
        return (httpCode, htmlBody)


if __name__ == "__main__":
    try:
        testWebApp = contentApp("localhost", 1234)
    except KeyboardInterrupt:
        print("Closing binded socket")
