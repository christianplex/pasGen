# Use Nginx to serve the static content
FROM nginx:alpine

# Copy the static files to the nginx html directory
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Configure nginx to listen on port 8080
RUN sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/conf.d/default.conf

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
