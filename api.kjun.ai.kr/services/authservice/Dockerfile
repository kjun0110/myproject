# Build stage
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
RUN apk add --no-cache bash
COPY gradlew .
COPY gradle gradle
COPY build.gradle ./
COPY services services
RUN chmod +x ./gradlew
RUN echo "rootProject.name = 'api'" > settings.gradle && \
    echo "" >> settings.gradle && \
    echo "include 'services:authservice'" >> settings.gradle
RUN ./gradlew :services:authservice:bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jdk-alpine
VOLUME /tmp
COPY --from=build /app/services/authservice/build/libs/*.jar auth-service.jar
ENTRYPOINT ["java", "-jar", "/auth-service.jar"]
