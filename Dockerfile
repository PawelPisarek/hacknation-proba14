# Aplikacja MVP „Różnica RTG” na ksefbot.pl (Coolify): ekran + przekazanie do usługi na karcie OMENa.
# Bez liczenia w kontenerze — wynik liczy usługa usluga/serwer.py na karcie (sieć lokalna).
FROM node:22-alpine
WORKDIR /app
COPY aplikacja/ ./aplikacja/
ENV PORT=3000 OMEN_URL=http://omen:8770
EXPOSE 3000
USER node
CMD ["node", "aplikacja/serwer.mjs"]
