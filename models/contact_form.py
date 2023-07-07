from pydantic import BaseModel, Field, EmailStr


class ContactForm(BaseModel):
    email: EmailStr = Field(
        title="Email Address",
        description="Your email address"
    )
    subject: str = Field(
        title="Subject",
        description="Subject of your message",
        max_length=100,
        min_length=1
    )
    message: str = Field(
        title="Message",
        description="Your message",
        max_length=2000,
        min_length=1
    )
