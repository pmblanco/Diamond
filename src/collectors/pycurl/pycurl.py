# coding=utf-8

"""
Collect statistics from a HTTP or HTTPS connexion

#### Dependencies

 * pycurl

#### Usage
Add the collector config as :

enabled = True
ttl_multiplier = 2
path_suffix = ""
measure_collector_time = False
byte_unit = byte,
req_vhost = www.my_server.com
req_url = https://www.my_server.com/, https://www.my_server.com/assets/jquery.js

Metrics are collected as :
    - servers.<hostname>.http.<url>.size (size of the page received in bytes)
    - servers.<hostname>.http.<url>.time (time to download the page in microsec)

    '.' and '/' chars are replaced by __, url looking like
       http://www.site.com/admin/page.html are replaced by
       http:__www_site_com_admin_page_html
"""

import pycurl
import diamond.collector
import datetime


class PycurlCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(PycurlCollector, self).get_default_config_help()
        config_help.update({
            'req_port': 'Port',
            'req_url':
            'array of full URL to get (ex : https://www.ici.net/mypage.html)',
            'req_vhost':
            'Host header variable if needed. Will be added to every request',
        })
        return config_help

    def get_default_config(self):
        default_config = super(PycurlCollector, self).get_default_config()
        default_config['path'] = 'pycurl'
        default_config['req_vhost'] = ''
        default_config['req_url'] = ['http://localhost/']

        default_config['headers'] = {'User-Agent': 'Diamond HTTP collector', }
        default_config['pycurl_metrics'] = ['TOTAL_TIME','CONNECT_TIME','PRETRANSFER_TIME','STARTTRANSFER_TIME','NAMELOOKUP_TIME']
        return default_config

    def collect(self):
        # create urllib2 vars
        if self.config['req_vhost'] != "":
            self.config['headers']['Host'] = self.config['req_vhost']

        # time the request
        for url in self.config['req_url']:
            self.log.debug("collecting %s", str(url))
#            req_start = datetime.datetime.now()
#            req = urllib2.Request(url, headers=self.config['headers'])
            try:
#                handle = urllib2.urlopen(req)
#                the_page = handle.read()
#                req_end = datetime.datetime.now()
#                 req_time = req_end - req_start
                c = pycurl.Curl()
                c.setopt(c.URL, url)
                c.setopt(c.WRITEFUNCTION, lambda x: None)
                c.setopt(c.VERBOSE,0)
                c.perform()

#                for curl_stat in curl_stats:
#                    #print('%s: %s' % (curl_stat,c.getinfo(curl_stat)))
#                     print('%s: %s' %  (curl_stat,c.getinfo(getattr(c,curl_stat))))


                # build a compatible name : no '.' and no'/' in the name
                metric_name = url.replace(
                    '/', '_').replace(
                    '.', '_').replace(
                    '\\', '').replace(
                    ':', '')
#                # metric_name = url.split("/")[-1].replace(".", "_")
                if metric_name == '':
                    metric_name = "root"
#                self.publish_gauge(
#                    metric_name + '.time',
#                    req_time.seconds * 1000000 + req_time.microseconds)
#                self.publish_gauge(
#                    metric_name + '.size',
#                    len(the_page))
              
                for pycurl_metric in self.config['pycurl_metrics']:
                    self.publish_gauge(
                         metric_name + '.' + pycurl_metric,
                         str(c.getinfo(getattr(c,pycurl_metric))* 1000000).rstrip('.0') )

            except IOError, e:
                self.log.error("Unable to open %s",
                               self.config['req_url'])
            except Exception, e:
                self.log.error("Unknown error opening url: %s", e)