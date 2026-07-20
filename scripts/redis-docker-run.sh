docker run -d \
-p 6379:6379 \
--restart=unless-stopped \
--name=redis redis