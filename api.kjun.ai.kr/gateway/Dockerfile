# Build stage
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
RUN apk add --no-cache bash
COPY gradlew .
COPY gradle gradle
COPY build.gradle ./
COPY gateway gateway
RUN chmod +x ./gradlew
RUN echo "rootProject.name = 'api'" > settings.gradle && \
    echo "" >> settings.gradle && \
    echo "include 'gateway'" >> settings.gradle
RUN ./gradlew :gateway:bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jdk-alpine
VOLUME /tmp
COPY --from=build /app/gateway/build/libs/*.jar gateway.jar
ENTRYPOINT ["java", "-jar", "/gateway.jar"]
