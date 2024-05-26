import org.jetbrains.kotlin.gradle.tasks.KotlinCompile
import java.net.URI

plugins {
    kotlin("jvm") version "1.7.20"
    id("org.sonarqube") version "3.0"
    id("com.github.johnrengelman.shadow") version "7.0.0"
}

group = "sk.happypc"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    maven { url = URI.create("https://jitpack.io") }
}

dependencies {
    implementation("jakarta.ws.rs:jakarta.ws.rs-api:3.1.0")
    implementation("jakarta.persistence:jakarta.persistence-api:3.1.0")

    implementation("org.apache.commons:commons-text:1.10.0")

    testImplementation(kotlin("test"))
    implementation(kotlin("stdlib-jdk8"))
    implementation(kotlin("reflect"))

    compileOnly("org.keycloak:keycloak-server-spi:22.0.5")
    compileOnly("org.keycloak:keycloak-core:22.0.5")
    compileOnly("org.keycloak:keycloak-services:22.0.5")
    compileOnly("org.keycloak:keycloak-server-spi-private:22.0.5")
    compileOnly("org.keycloak:keycloak-model-jpa:22.0.5")

    implementation("com.beust:klaxon:5.6")
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:adapter-rxjava2:2.9.0")
    implementation("com.squareup.retrofit2:converter-jackson:2.9.0")

    implementation("org.bouncycastle:bcprov-jdk18on:1.76")

//    testImplementation("junit:junit:4.13.2")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.2.0")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.2.0")
    testImplementation("org.junit.platform:junit-platform-console:1.2.0")

    testImplementation("org.keycloak:keycloak-server-spi:22.0.5")
    testImplementation("org.keycloak:keycloak-core:22.0.5")
    testImplementation("org.keycloak:keycloak-services:22.0.5")
    testImplementation("org.keycloak:keycloak-server-spi-private:22.0.5")

    testImplementation("org.testcontainers:junit-jupiter:1.19.1")
    testImplementation(platform("org.junit:junit-bom:5.10.1"))
    testImplementation("org.testcontainers:testcontainers:1.19.1")

    testImplementation("io.ktor:ktor-client-core:2.1.2")
    testImplementation("io.ktor:ktor-client-cio:2.1.2")

    testImplementation("com.github.dasniko:testcontainers-keycloak:3.1.0")
//    testImplementation("org.mockito:mockito-core:5.7.0")

    implementation("com.google.guava:guava:32.1.3-jre")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "1.8"
    kotlinOptions.freeCompilerArgs = listOf("-Xjsr305=strict")
}

tasks.withType<Jar> {
    exclude("META-INF/*.SF", "META-INF/*.DSA", "META-INF/*.RSA", "META-INF/*.MF")
    duplicatesStrategy = org.gradle.api.file.DuplicatesStrategy.EXCLUDE
    archiveBaseName.set("mobile-otp-plugin")
    from(configurations.runtimeClasspath.get().map { if (it.isDirectory) it else zipTree(it) })
}