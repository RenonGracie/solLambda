#!/bin/bash

# migration_helper.sh - Helper script for managing Alembic migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in the right directory
check_environment() {
    if [ ! -f "alembic.ini" ]; then
        print_error "alembic.ini not found. Please run this script from the project root."
        exit 1
    fi
    
    if [ ! -d "migrations" ]; then
        print_error "migrations directory not found. Please run this script from the project root."
        exit 1
    fi
}

# Function to generate a new migration
generate_migration() {
    local message="$1"
    if [ -z "$message" ]; then
        print_error "Migration message is required"
        echo "Usage: $0 generate \"your migration message\""
        exit 1
    fi
    
    print_status "Generating new migration: $message"
    uv run alembic revision --autogenerate -m "$message"
    print_success "Migration generated successfully"
}

# Function to run migrations
run_migration() {
    local environment="$1"
    
    print_status "Running migrations for environment: ${environment:-local}"
    
    # Set environment variables based on target
    case "$environment" in
        "dev")
            print_status "Using development environment settings"
            export ENV=dev
            ;;
        "stg")
            print_status "Using staging environment settings"
            export ENV=stg
            ;;
        "prod")
            print_warning "Running migrations in PRODUCTION environment"
            read -p "Are you sure you want to run migrations in production? (yes/no): " confirm
            if [ "$confirm" != "yes" ]; then
                print_status "Migration cancelled"
                exit 0
            fi
            export ENV=prod
            ;;
        "local")
            print_status "Using local environment settings"
            export ENV=dev
            ;;
        *)
            print_warning "No environment specified, using local development settings"
            export ENV=dev
            ;;
    esac
    
    # Run the migration
    uv run alembic upgrade head
    print_success "Migration completed successfully"
}

# Function to check migration status
check_status() {
    print_status "Checking migration status..."
    uv run alembic current
    echo ""
    print_status "Available migrations:"
    uv run alembic history
}

# Function to rollback migration
rollback_migration() {
    local steps="${1:-1}"
    print_warning "Rolling back $steps migration(s)"
    read -p "Are you sure you want to rollback? This may cause data loss. (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_status "Rollback cancelled"
        exit 0
    fi
    
    uv run alembic downgrade -$steps
    print_success "Rollback completed"
}

# Function to deploy with migration
deploy_with_migration() {
    local environment="$1"
    
    if [ -z "$environment" ]; then
        print_error "Environment is required"
        echo "Usage: $0 deploy <dev|stg|prod>"
        exit 1
    fi
    
    print_status "Deploying to $environment with migrations..."
    
    # Deploy the application
    print_status "Deploying application..."
    serverless deploy --stage "$environment"
    
    # Run migrations via Lambda
    print_status "Running migrations via Lambda..."
    aws lambda invoke \
        --function-name "SolHealth-BE-${environment}-migrate" \
        --region us-east-2 \
        --payload '{}' \
        --cli-binary-format raw-in-base64-out \
        response.json
    
    # Check the response
    if [ -f "response.json" ]; then
        print_status "Migration response:"
        cat response.json
        rm response.json
    fi
    
    print_success "Deployment with migrations completed"
}

# Main script logic
main() {
    check_environment
    
    case "$1" in
        "generate")
            generate_migration "$2"
            ;;
        "migrate")
            run_migration "$2"
            ;;
        "status")
            check_status
            ;;
        "rollback")
            rollback_migration "$2"
            ;;
        "deploy")
            deploy_with_migration "$2"
            ;;
        "help"|"--help"|"-h")
            echo "Migration Helper Script"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  generate \"message\"     Generate a new migration"
            echo "  migrate [env]          Run migrations (env: local|dev|stg|prod)"
            echo "  status                 Check current migration status"
            echo "  rollback [steps]       Rollback migrations (default: 1 step)"
            echo "  deploy <env>           Deploy application with migrations"
            echo "  help                   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 generate \"add payment type column\""
            echo "  $0 migrate dev"
            echo "  $0 deploy stg"
            echo "  $0 rollback 2"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run the main function with all arguments
main "$@"