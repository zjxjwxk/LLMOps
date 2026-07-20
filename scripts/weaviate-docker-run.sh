docker run -d --name weaviate \
--restart=unless-stopped \
-v weaviate_data:/var/lib/weaviate \
-p 8080:8080 \
-p 50051:50051 \
cr.weaviate.io/semitechnologies/weaviate:1.37.2