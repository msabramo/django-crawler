curl -s -k -X POST --data-binary @- http://localhost:8000/crawl/ <<EOF
http://www.dotcloud.com/
http://www.cnn.com/
http://www.4chan.org/
EOF
