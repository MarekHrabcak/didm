FROM mcr.microsoft.com/dotnet/aspnet:8.0-jammy as build
WORKDIR /app

# RUN apt-get update \
#     && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#         ca-certificates \
#         \
#         # .NET dependencies
#         curl \
#         libc6 \
#         libgcc1 \
#         libgssapi-krb5-2 \
#         # libicu66 \
#         # libssl1.1 \
#         libstdc++6 \
#         zlib1g \
#     && rm -rf /var/lib/apt/lists/*
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y dotnet-sdk-8.0
# # Install .NET
# ENV DOTNET_VERSION=8.0.0

# RUN curl -fSL --output dotnet.tar.gz https://dotnetcli.azureedge.net/dotnet/Runtime/$DOTNET_VERSION/dotnet-runtime-$DOTNET_VERSION-linux-x64.tar.gz \
#     && mkdir -p /usr/share/dotnet \
#     && tar -zxf dotnet.tar.gz -C /usr/share/dotnet \
#     && rm dotnet.tar.gz \
#     && ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet

# Copy csproj and restore distinct layers
COPY *.sln .
COPY FaberController/*.csproj ./FaberController/
RUN dotnet restore

# Copy and build app
COPY FaberController/. ./FaberController/
WORKDIR /app/FaberController
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:8.0 as runtime
WORKDIR /app
COPY --from=build /app/FaberController/out ./
ENTRYPOINT ["dotnet", "FaberController.dll"]