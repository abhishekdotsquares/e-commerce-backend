import strawberry
from api.v1.companies.Mutation.mutation import CompanyMutation
from api.v1.companies.Query.query import CompanyQuery
from api.v1.enquiry.Mutation.mutation import EnquiryMutation
from api.v1.enquiry.Query.query import EnquiryQuery
from api.v1.users.Mutation.mutation import UserMutation


@strawberry.type
class Query(CompanyQuery,EnquiryQuery):
    pass 

@strawberry.type
class Mutation(CompanyMutation, UserMutation,EnquiryMutation):
    pass 
# Define the GraphQL Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
