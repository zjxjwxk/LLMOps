docker run \
--name postgres-dev \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=19981018 \
-v /var/lib/postgresql/postgresql-dev:/var/lib/postgresql \
-p 5432:5432 \
-d postgres