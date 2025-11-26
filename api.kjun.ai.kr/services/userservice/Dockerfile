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
    echo "include 'services:userservice'" >> settings.gradle
RUN ./gradlew :services:userservice:bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jdk-alpine
VOLUME /tmp
COPY --from=build /app/services/userservice/build/libs/*.jar user-service.jar
ENTRYPOINT ["java", "-jar", "/user-service.jar"]
