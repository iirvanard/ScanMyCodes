PGDMP  /    1             
    |         	   iirvanard #   16.4 (Ubuntu 16.4-0ubuntu0.24.04.1) #   16.4 (Ubuntu 16.4-0ubuntu0.24.04.1) :    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16389 	   iirvanard    DATABASE     u   CREATE DATABASE iirvanard WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';
    DROP DATABASE iirvanard;
                postgres    false            �            1259    19924    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    postgres    false            �            1259    19930    analyze_issue    TABLE     �   CREATE TABLE public.analyze_issue (
    id integer NOT NULL,
    project_id uuid NOT NULL,
    branch integer NOT NULL,
    path_ character varying NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
 !   DROP TABLE public.analyze_issue;
       public         heap    postgres    false            �            1259    19929    analyze_issue_id_seq    SEQUENCE     �   CREATE SEQUENCE public.analyze_issue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.analyze_issue_id_seq;
       public          postgres    false    227            �           0    0    analyze_issue_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.analyze_issue_id_seq OWNED BY public.analyze_issue.id;
          public          postgres    false    226            �            1259    19948    collaborator_access    TABLE     �   CREATE TABLE public.collaborator_access (
    id uuid NOT NULL,
    collaborator_id uuid NOT NULL,
    branch_id integer NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
 '   DROP TABLE public.collaborator_access;
       public         heap    postgres    false            �            1259    19867 
   git_branch    TABLE     a  CREATE TABLE public.git_branch (
    id integer NOT NULL,
    remote character varying NOT NULL,
    project_id uuid NOT NULL,
    git_repository_id integer NOT NULL,
    latest_commits character varying NOT NULL,
    last_analyzed_at timestamp without time zone,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
    DROP TABLE public.git_branch;
       public         heap    postgres    false            �            1259    19866    git_branch_id_seq    SEQUENCE     �   CREATE SEQUENCE public.git_branch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.git_branch_id_seq;
       public          postgres    false    224            �           0    0    git_branch_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.git_branch_id_seq OWNED BY public.git_branch.id;
          public          postgres    false    223            �            1259    19798    git_repository    TABLE     J  CREATE TABLE public.git_repository (
    id integer NOT NULL,
    privacy boolean NOT NULL,
    access_token character varying,
    repo_url character varying NOT NULL,
    default_branch character varying(30),
    project_id uuid NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
 "   DROP TABLE public.git_repository;
       public         heap    postgres    false            �            1259    19797    git_repository_id_seq    SEQUENCE     �   CREATE SEQUENCE public.git_repository_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.git_repository_id_seq;
       public          postgres    false    219            �           0    0    git_repository_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.git_repository_id_seq OWNED BY public.git_repository.id;
          public          postgres    false    218            �            1259    19813    openai_project    TABLE     5  CREATE TABLE public.openai_project (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    openai_model character varying NOT NULL,
    openai_key character varying NOT NULL,
    openai_url character varying NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
 "   DROP TABLE public.openai_project;
       public         heap    postgres    false            �            1259    19827    project_collaborators    TABLE     "  CREATE TABLE public.project_collaborators (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    collaborator_id integer NOT NULL,
    inviter_id integer NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone,
    status character varying(20)
);
 )   DROP TABLE public.project_collaborators;
       public         heap    postgres    false            �            1259    19849    project_log    TABLE     ?  CREATE TABLE public.project_log (
    id uuid NOT NULL,
    project_id uuid NOT NULL,
    user_id integer NOT NULL,
    type character varying NOT NULL,
    status character varying NOT NULL,
    path_ character varying NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
    DROP TABLE public.project_log;
       public         heap    postgres    false            �            1259    19785    projects    TABLE     �  CREATE TABLE public.projects (
    project_id uuid NOT NULL,
    user_id integer NOT NULL,
    fetch_status character varying NOT NULL,
    analyze_status character varying NOT NULL,
    analysis_request_at date,
    description text,
    project_name character varying(255) NOT NULL,
    fetched_at date,
    analyze_at date,
    source character varying(50) NOT NULL,
    updated_at timestamp without time zone,
    created_at timestamp without time zone
);
    DROP TABLE public.projects;
       public         heap    postgres    false            �            1259    19773    users    TABLE     �  CREATE TABLE public.users (
    id integer NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    image_profile character varying(2048),
    username character varying(12) NOT NULL,
    email character varying NOT NULL,
    password character varying NOT NULL,
    update_at timestamp without time zone,
    created_at timestamp without time zone
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    19772    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          postgres    false    216            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          postgres    false    215            �           2604    19933    analyze_issue id    DEFAULT     t   ALTER TABLE ONLY public.analyze_issue ALTER COLUMN id SET DEFAULT nextval('public.analyze_issue_id_seq'::regclass);
 ?   ALTER TABLE public.analyze_issue ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    226    227    227            �           2604    19870    git_branch id    DEFAULT     n   ALTER TABLE ONLY public.git_branch ALTER COLUMN id SET DEFAULT nextval('public.git_branch_id_seq'::regclass);
 <   ALTER TABLE public.git_branch ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    223    224    224            �           2604    19801    git_repository id    DEFAULT     v   ALTER TABLE ONLY public.git_repository ALTER COLUMN id SET DEFAULT nextval('public.git_repository_id_seq'::regclass);
 @   ALTER TABLE public.git_repository ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    219    218    219            �           2604    19776    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    215    216    216                       2606    19876    git_branch _project_remote_uc 
   CONSTRAINT     f   ALTER TABLE ONLY public.git_branch
    ADD CONSTRAINT _project_remote_uc UNIQUE (project_id, remote);
 G   ALTER TABLE ONLY public.git_branch DROP CONSTRAINT _project_remote_uc;
       public            postgres    false    224    224                       2606    19928 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            postgres    false    225                       2606    19937     analyze_issue analyze_issue_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.analyze_issue
    ADD CONSTRAINT analyze_issue_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.analyze_issue DROP CONSTRAINT analyze_issue_pkey;
       public            postgres    false    227                       2606    19952 ,   collaborator_access collaborator_access_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.collaborator_access
    ADD CONSTRAINT collaborator_access_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.collaborator_access DROP CONSTRAINT collaborator_access_pkey;
       public            postgres    false    228                       2606    19874    git_branch git_branch_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.git_branch
    ADD CONSTRAINT git_branch_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.git_branch DROP CONSTRAINT git_branch_pkey;
       public            postgres    false    224            	           2606    19805 "   git_repository git_repository_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.git_repository
    ADD CONSTRAINT git_repository_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.git_repository DROP CONSTRAINT git_repository_pkey;
       public            postgres    false    219                       2606    19807 ,   git_repository git_repository_project_id_key 
   CONSTRAINT     m   ALTER TABLE ONLY public.git_repository
    ADD CONSTRAINT git_repository_project_id_key UNIQUE (project_id);
 V   ALTER TABLE ONLY public.git_repository DROP CONSTRAINT git_repository_project_id_key;
       public            postgres    false    219                       2606    19819 "   openai_project openai_project_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.openai_project
    ADD CONSTRAINT openai_project_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.openai_project DROP CONSTRAINT openai_project_pkey;
       public            postgres    false    220                       2606    19821 ,   openai_project openai_project_project_id_key 
   CONSTRAINT     m   ALTER TABLE ONLY public.openai_project
    ADD CONSTRAINT openai_project_project_id_key UNIQUE (project_id);
 V   ALTER TABLE ONLY public.openai_project DROP CONSTRAINT openai_project_project_id_key;
       public            postgres    false    220                       2606    19831 0   project_collaborators project_collaborators_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.project_collaborators
    ADD CONSTRAINT project_collaborators_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.project_collaborators DROP CONSTRAINT project_collaborators_pkey;
       public            postgres    false    221                       2606    19855    project_log project_log_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.project_log
    ADD CONSTRAINT project_log_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.project_log DROP CONSTRAINT project_log_pkey;
       public            postgres    false    222                       2606    19791    projects projects_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);
 @   ALTER TABLE ONLY public.projects DROP CONSTRAINT projects_pkey;
       public            postgres    false    217                       2606    19966     projects projects_project_id_key 
   CONSTRAINT     a   ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_project_id_key UNIQUE (project_id);
 J   ALTER TABLE ONLY public.projects DROP CONSTRAINT projects_project_id_key;
       public            postgres    false    217            !           2606    19954 .   collaborator_access unique_collaborator_branch 
   CONSTRAINT        ALTER TABLE ONLY public.collaborator_access
    ADD CONSTRAINT unique_collaborator_branch UNIQUE (collaborator_id, branch_id);
 X   ALTER TABLE ONLY public.collaborator_access DROP CONSTRAINT unique_collaborator_branch;
       public            postgres    false    228    228                       2606    19833 1   project_collaborators unique_project_collaborator 
   CONSTRAINT     �   ALTER TABLE ONLY public.project_collaborators
    ADD CONSTRAINT unique_project_collaborator UNIQUE (project_id, collaborator_id);
 [   ALTER TABLE ONLY public.project_collaborators DROP CONSTRAINT unique_project_collaborator;
       public            postgres    false    221    221            �           2606    19782    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public            postgres    false    216                       2606    19780    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    216                       2606    19784    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            postgres    false    216            ,           2606    19938 '   analyze_issue analyze_issue_branch_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.analyze_issue
    ADD CONSTRAINT analyze_issue_branch_fkey FOREIGN KEY (branch) REFERENCES public.git_branch(id) ON DELETE CASCADE;
 Q   ALTER TABLE ONLY public.analyze_issue DROP CONSTRAINT analyze_issue_branch_fkey;
       public          postgres    false    224    227    3353            -           2606    19943 +   analyze_issue analyze_issue_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.analyze_issue
    ADD CONSTRAINT analyze_issue_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
 U   ALTER TABLE ONLY public.analyze_issue DROP CONSTRAINT analyze_issue_project_id_fkey;
       public          postgres    false    217    227    3333            .           2606    19955 6   collaborator_access collaborator_access_branch_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.collaborator_access
    ADD CONSTRAINT collaborator_access_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.git_branch(id) ON DELETE CASCADE;
 `   ALTER TABLE ONLY public.collaborator_access DROP CONSTRAINT collaborator_access_branch_id_fkey;
       public          postgres    false    228    224    3353            /           2606    19960 <   collaborator_access collaborator_access_collaborator_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.collaborator_access
    ADD CONSTRAINT collaborator_access_collaborator_id_fkey FOREIGN KEY (collaborator_id) REFERENCES public.project_collaborators(id);
 f   ALTER TABLE ONLY public.collaborator_access DROP CONSTRAINT collaborator_access_collaborator_id_fkey;
       public          postgres    false    3345    228    221            *           2606    19877 ,   git_branch git_branch_git_repository_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.git_branch
    ADD CONSTRAINT git_branch_git_repository_id_fkey FOREIGN KEY (git_repository_id) REFERENCES public.git_repository(id) ON DELETE CASCADE;
 V   ALTER TABLE ONLY public.git_branch DROP CONSTRAINT git_branch_git_repository_id_fkey;
       public          postgres    false    224    219    3337            +           2606    19882 %   git_branch git_branch_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.git_branch
    ADD CONSTRAINT git_branch_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
 O   ALTER TABLE ONLY public.git_branch DROP CONSTRAINT git_branch_project_id_fkey;
       public          postgres    false    3333    217    224            #           2606    19808 -   git_repository git_repository_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.git_repository
    ADD CONSTRAINT git_repository_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id) ON DELETE CASCADE;
 W   ALTER TABLE ONLY public.git_repository DROP CONSTRAINT git_repository_project_id_fkey;
       public          postgres    false    3333    217    219            $           2606    19822 -   openai_project openai_project_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.openai_project
    ADD CONSTRAINT openai_project_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);
 W   ALTER TABLE ONLY public.openai_project DROP CONSTRAINT openai_project_project_id_fkey;
       public          postgres    false    217    220    3333            %           2606    19834 @   project_collaborators project_collaborators_collaborator_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.project_collaborators
    ADD CONSTRAINT project_collaborators_collaborator_id_fkey FOREIGN KEY (collaborator_id) REFERENCES public.users(id) ON DELETE CASCADE;
 j   ALTER TABLE ONLY public.project_collaborators DROP CONSTRAINT project_collaborators_collaborator_id_fkey;
       public          postgres    false    3329    221    216            &           2606    19839 ;   project_collaborators project_collaborators_inviter_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.project_collaborators
    ADD CONSTRAINT project_collaborators_inviter_id_fkey FOREIGN KEY (inviter_id) REFERENCES public.users(id) ON DELETE CASCADE;
 e   ALTER TABLE ONLY public.project_collaborators DROP CONSTRAINT project_collaborators_inviter_id_fkey;
       public          postgres    false    216    221    3329            '           2606    19844 ;   project_collaborators project_collaborators_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.project_collaborators
    ADD CONSTRAINT project_collaborators_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);
 e   ALTER TABLE ONLY public.project_collaborators DROP CONSTRAINT project_collaborators_project_id_fkey;
       public          postgres    false    3333    221    217            (           2606    19856 '   project_log project_log_project_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.project_log
    ADD CONSTRAINT project_log_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);
 Q   ALTER TABLE ONLY public.project_log DROP CONSTRAINT project_log_project_id_fkey;
       public          postgres    false    3333    217    222            )           2606    19861 $   project_log project_log_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.project_log
    ADD CONSTRAINT project_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 N   ALTER TABLE ONLY public.project_log DROP CONSTRAINT project_log_user_id_fkey;
       public          postgres    false    222    216    3329            "           2606    19792    projects projects_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 H   ALTER TABLE ONLY public.projects DROP CONSTRAINT projects_user_id_fkey;
       public          postgres    false    216    217    3329           