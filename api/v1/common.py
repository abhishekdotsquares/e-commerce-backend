import strawberry
from api.v1.companies.Mutation.mutation import CompanyMutation
from api.v1.companies.Query.query import CompanyQuery
from api.v1.users.Mutation.mutation import UserMutation

from api.v1.subscription_plans.Query.query import PlanQuery
from api.v1.subscription_plans.Mutation.mutation import PlanMutation

@strawberry.type
class Query(CompanyQuery, PlanQuery):
    pass 

@strawberry.type
class Mutation(CompanyMutation, UserMutation, PlanMutation):
    pass 
# Define the GraphQL Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
