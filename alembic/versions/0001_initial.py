from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('global_role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)

    op.create_table(
        'team',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
    )
    op.create_index('ix_team_code', 'team', ['code'], unique=True)

    op.create_table(
        'user_teams',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), primary_key=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('team.id'), primary_key=True),
        sa.Column('role_in_team', sa.String(length=20), nullable=False, server_default='user'),
    )

    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('open', 'in_progress', 'done', name='taskstatus'), nullable=False, server_default='open'),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_task_team_status_deadline', 'task', ['team_id', 'status', 'deadline'])

    op.create_table(
        'taskcomment',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('task.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'meeting',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_meeting_team_time', 'meeting', ['team_id', 'starts_at', 'ends_at'])

    op.create_table(
        'evaluation',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('task.id'), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('task_id', 'evaluator_id', name='uq_evaluation_task_evaluator'),
    )

def downgrade() -> None:
    op.drop_table('evaluation')
    op.drop_index('ix_meeting_team_time', table_name='meeting')
    op.drop_table('meeting')
    op.drop_table('taskcomment')
    op.drop_index('ix_task_team_status_deadline', table_name='task')
    op.drop_table('task')
    op.drop_table('user_teams')
    op.drop_index('ix_team_code', table_name='team')
    op.drop_table('team')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
